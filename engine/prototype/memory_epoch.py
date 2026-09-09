"""Immutable, caller-pinned history roots independent of the mutable search DB.

An epoch covers exactly the caller's supplied references. It cannot attest that
history omitted before creation ever existed. Raw storage and the pinned root
must remain intact. Publication returns a root only after complete validation.
"""
import base64
import json
import time
from workflow_memory import identity

VERSION='helix.memory.epoch.v1'


def encode(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def freeze(memory,project,refs,max_bytes=10485760):
    started=time.perf_counter();before=dict(memory.store.metrics)
    if not isinstance(refs,list) or not refs or any(not isinstance(r,str) for r in refs) or len(set(refs))!=len(refs):raise ValueError('Unique nonempty references required')
    records=memory.retrieve(project,refs,max_bytes=max_bytes)
    entries=[]
    for record in records:
        entry={k:record[k] for k in ('record_hash','source_hash','project','session','event_id','bytes')}
        entries.append(entry)
    epoch={'schema':VERSION,'project':project,'records':entries,'count':len(entries),
           'source_bytes':sum(e['bytes'] for e in entries),'coverage':'Exactly caller-supplied references, in caller order; no claim about omitted pre-epoch history.'}
    raw=encode(epoch);key=memory.store.put(raw)['sha256']
    # Validate independently through the index-free reader before returning.
    read(memory.store,key,project,refs,max_bytes=max_bytes)
    return {'epoch_sha256':key,'project':project,'count':len(entries),'source_bytes':epoch['source_bytes'],
            'seconds':time.perf_counter()-started,'store_io':{k:memory.store.metrics[k]-before[k] for k in before},
            'scope':'Logical store I/O; SQLite/physical traffic and inference costs unmeasured.'}


def load(store,root,project):
    identity(project)
    epoch=json.loads(store.get(root))
    if not isinstance(epoch,dict):raise ValueError('Invalid epoch object')
    if epoch.get('schema')!=VERSION or epoch.get('project')!=project:raise ValueError('Epoch scope or version mismatch')
    entries=epoch.get('records')
    if not isinstance(entries,list) or not entries or type(epoch.get('count')) is not int or epoch['count']!=len(entries):raise ValueError('Invalid epoch count')
    seen=set();total=0
    for entry in entries:
        if not isinstance(entry,dict) or set(entry)!={'record_hash','source_hash','project','session','event_id','bytes'}:raise ValueError('Invalid epoch entry')
        if entry['project']!=project or type(entry['bytes']) is not int or entry['bytes']<0:raise ValueError('Invalid epoch identity/length')
        identity(entry['session'],entry['event_id'])
        ref=entry['record_hash']
        if not isinstance(ref,str) or ref in seen:raise ValueError('Duplicate epoch identity')
        seen.add(ref);total+=entry['bytes']
    if type(epoch.get('source_bytes')) is not int or total!=epoch['source_bytes']:raise ValueError('Epoch byte count mismatch')
    return epoch


def read(store,root,project,refs,max_bytes=1048576):
    """All requested exact records or error; no state publication or repair."""
    if not isinstance(refs,list) or not refs or any(not isinstance(r,str) for r in refs) or len(set(refs))!=len(refs):raise ValueError('Unique references required')
    if type(max_bytes) is not int or max_bytes<0:raise ValueError('Invalid retrieval limit')
    epoch=load(store,root,project);catalog={e['record_hash']:e for e in epoch['records']}
    if any(ref not in catalog for ref in refs):raise ValueError('Record not covered by pinned epoch')
    selected=[catalog[ref] for ref in refs]
    if sum(e['bytes'] for e in selected)>max_bytes:raise ValueError('Exact retrieval exceeds limit; no silent truncation')
    result=[]
    for entry in selected:
        header=json.loads(store.get(entry['record_hash']))
        if header.get('schema')!='helix.memory.record.v1' or any(header.get(k)!=entry[k] for k in ('source_hash','project','session','event_id')) or type(header.get('bytes')) is not int or header['bytes']!=entry['bytes']:raise ValueError('Epoch/header mismatch')
        raw=store.get(entry['source_hash'])
        if len(raw)!=entry['bytes']:raise ValueError('Epoch/source mismatch')
        result.append({**entry,'raw':raw})
    return result


def page(store,root,project,offset=0,limit=50,max_bytes=1048576):
    if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=100:raise ValueError('Invalid page')
    epoch=load(store,root,project)
    if offset>epoch['count']:raise ValueError('Cursor past epoch')
    selected=epoch['records'][offset:offset+limit]
    records=read(store,root,project,[e['record_hash'] for e in selected],max_bytes) if selected else []
    values=[]
    for record in records:
        try:body={'text':record['raw'].decode('utf-8')}
        except UnicodeDecodeError:body={'base64':base64.b64encode(record['raw']).decode()}
        values.append({k:record[k] for k in ('record_hash','session','event_id')}|body)
    cursor=offset+len(records)
    return {'epoch_sha256':root,'records':values,'next_offset':cursor,'has_more':cursor<epoch['count'],
            'coverage':'Exact page in immutable epoch order; later epochs are separate.'}


def verify_live_catalog(memory,root,project):
    """Detect lost/changed indexed records covered by this epoch; allow new ones."""
    epoch=load(memory.store,root,project)
    with memory.db() as db:
        db.execute('BEGIN') # One read snapshot across the complete covered catalog.
        for entry in epoch['records']:
            row=db.execute('SELECT project,session,event_id FROM events WHERE record_hash=?',(entry['record_hash'],)).fetchone()
            if row!=(entry['project'],entry['session'],entry['event_id']):raise ValueError('Live catalog no longer covers pinned epoch; use epoch recovery')
    return {'covered':epoch['count'],'new_records_allowed':True,'epoch_sha256':root}
