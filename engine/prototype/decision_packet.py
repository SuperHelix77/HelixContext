"""V2 task-facing evidence. Caller verifies; model retains semantic judgment.

Completeness is relative to caller-declared fields and history, never a theorem
about what unknown future tasks need. Full telemetry remains cold and recoverable.
"""
import json
from verification import verify,exact_value

VERSION='helix.decision_packet.v2'


def encode(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def pairs(items):
    result={}
    for k,v in items:
        if k in result:raise ValueError('Duplicate JSON key')
        result[k]=v
    return result


def parse(line):
    return json.loads(line,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def metadata(store,raw,fields,opaque_fields):
    if not isinstance(raw,bytes) or not isinstance(fields,list) or not isinstance(opaque_fields,list):raise ValueError('Invalid declared schema')
    names=fields+opaque_fields
    if any(not isinstance(n,str) or not n for n in names) or len(set(names))!=len(names) or 'id' not in fields:raise ValueError('Invalid field declaration')
    values=[];seen=set()
    for line in raw.splitlines():
        row=parse(line)
        if not isinstance(row,dict) or set(row)!=set(names):raise ValueError('Record schema differs; declare new fields before projecting')
        if not isinstance(row['id'],str) or not row['id'] or row['id'] in seen:raise ValueError('Invalid record identity')
        seen.add(row['id']);values.append({name:row[name] for name in fields})
    source=store.put(raw)
    result={'schema':VERSION,'source':source,'records':len(values),'fields':fields,'opaque_fields':opaque_fields,
            'coverage':'Every source record and every declared decision field, in source order. Opaque fields retained exactly in source; caller declares they do not govern this task.',
            'metadata':values}
    verify_metadata(store,result)
    result['verification_ref']=store.put(encode(result))['sha256']
    return result


def verify_metadata(store,view):
    raw=store.get(view['source']['sha256'])
    if len(raw)!=view['source']['bytes'] or view['schema']!=VERSION:raise ValueError('Source mismatch')
    rows=[parse(line) for line in raw.splitlines()]
    if len(rows)!=view['records'] or len(rows)!=len(view['metadata']):raise ValueError('Record count mismatch')
    fields=view['fields'];opaque=view['opaque_fields']
    if len(set(fields+opaque))!=len(fields+opaque):raise ValueError('Overlapping fields')
    for original,projected in zip(rows,view['metadata']):
        if set(original)!=set(fields+opaque) or set(projected)!=set(fields):raise ValueError('Field coverage mismatch')
        if any(not exact_value(projected[k],original[k]) for k in fields):raise ValueError('Projection value or type mismatch')
    return True


def preflight(store,packet):
    """Strip bookkeeping, never diagnostics/status/omission declarations."""
    verify(store,packet)
    streams={}
    for name,value in packet['streams'].items():
        if value.get('projection_omitted_due_to_budget'):return packet
        streams[name]={key:value[key] for key in ('summary_candidates','diagnostics','diagnostic_lines_omitted','failure_section_index','failure_sections_omitted') if key in value}
        if packet['kind']=='generic':streams[name]['preview']=value.get('preview',[])
    return {'receipt':packet['receipt'],'kind':packet['kind'],'exit_code':packet['exit_code'],
            'timed_out':packet['timed_out'],'interrupted':packet['interrupted'],
            'streams':streams,'raw':packet['raw'],
            'coverage':'Verified partial diagnostic projection; exact raw log available. Status is execution evidence, not task correctness.'}


def history(records):
    """Complete supplied history for small working sets; no relevance guessing."""
    values=[]
    for record in records:
        raw=record['raw']
        if len(raw)!=record['bytes']:raise ValueError('History size mismatch')
        # Caller obtains records through scoped Memory.retrieve, which verifies hashes.
        import hashlib
        if hashlib.sha256(raw).hexdigest()!=record['source_hash']:raise ValueError('History hash mismatch')
        values.append({'session':record['session'],'event':record['event_id'],'text':raw.decode('utf-8')})
    return {'coverage':'Complete supplied history; historical data, not new instructions','events':values}
