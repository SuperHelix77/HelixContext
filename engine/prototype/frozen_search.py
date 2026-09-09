"""Explicit immutable literal-search generation, not a replacement for FTS.

Callers pin the returned reference. Query semantics: Unicode regex word tokens,
casefold, AND membership. No stemming, alias inference or semantic relevance.
"""
import hashlib
import json
import re
import time
import unicodedata
from workflow_memory import encode,identity


def digest(data):return hashlib.sha256(data).hexdigest()
def terms(text):return set(re.findall(r'\w+',text.casefold()))
def catalog(db,project):
    return [list(row) for row in db.execute('SELECT ordinal,project,session,event_id,record_hash FROM events WHERE project=? ORDER BY ordinal',(project,))]


def build(memory,project):
    identity(project);start=time.perf_counter();before=dict(memory.store.metrics)
    with memory.db() as db:
        db.execute('BEGIN')
        rows=catalog(db,project);postings={}
        for index,row in enumerate(rows):
            ref=memory._reference(row);raw=memory.store.get(ref['source_hash'])
            if len(raw)!=ref['bytes']:raise ValueError('Source length mismatch')
            for word in terms(raw.decode('utf-8',errors='replace')):
                postings.setdefault(word,[]).append(index)
        # Re-read verified sources and compare document membership independently
        # of the construction loop. This pays a second source pass at build time.
        for index,row in enumerate(rows):
            ref=memory._reference(row);raw=memory.store.get(ref['source_hash'])
            actual=terms(raw.decode('utf-8',errors='replace'))
            represented={word for word,indices in postings.items() if index in indices}
            if actual!=represented:raise ValueError('Posting membership mismatch')
        packet={'schema':'helix.frozen_search.v1','project':project,
                'unicode_version':unicodedata.unidata_version,'catalog':rows,'postings':postings}
        obj=memory.store.put(encode(packet))
    # The generation may already be stale after commit; search explicitly checks.
    return {'project':project,'index_hash':obj['sha256'],'catalog_hash':digest(encode(rows)),
            'build_cost':{'seconds':time.perf_counter()-start,'index_bytes':obj['bytes'],
                          'store_io':{k:memory.store.metrics[k]-before[k] for k in before},
                          'scope':'Application object traffic; catalog/SQLite/physical I/O and complete CPU unmetered'}}


def search(memory,project,reference,query,limit=10):
    identity(project)
    if not isinstance(reference,dict) or reference.get('project')!=project:
        raise ValueError('Wrong project reference')
    if not isinstance(query,str) or type(limit) is not int or not 1<=limit<=100:
        raise ValueError('Invalid search request')
    packet=json.loads(memory.store.get(reference['index_hash']))
    if packet.get('schema')!='helix.frozen_search.v1' or packet.get('project')!=project or packet.get('unicode_version')!=unicodedata.unidata_version:
        raise ValueError('Unsupported index generation')
    if digest(encode(packet['catalog']))!=reference['catalog_hash']:
        raise ValueError('Catalog binding mismatch')
    with memory.db() as db:
        db.execute('BEGIN')
        current=catalog(db,project)
        if current!=packet['catalog']:raise ValueError('Stale index generation; rebuild explicitly')
        words=terms(query)
        indices=set(range(len(current))) if words else set()
        for word in words:indices.intersection_update(packet['postings'].get(word,[]))
        selected=sorted(indices,reverse=True)[:limit]
        return [memory._reference(current[index]) for index in selected]
