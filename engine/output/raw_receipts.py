"""Capture a completed native rollout and index exact tool calls, never reasoning.

Raw history is private evidence. The index contains identities, byte spans and
hashes, not interpreted tool outcomes or a claim that all execution was observed.
"""
import hashlib,json
from pathlib import Path


def capture(source,out,thread_id):
    source=Path(source);out=Path(out)
    before=source.stat()
    if before.st_size>64_000_000:raise ValueError('Raw receipt exceeds 64MB bound')
    raw=source.read_bytes();after=source.stat()
    if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):
        raise ValueError('Raw receipt changed during capture')
    records=[];offset=0;identities=[]
    for line in raw.splitlines(keepends=True):
        event=json.loads(line);payload=event.get('payload',{})
        if event.get('type')=='session_meta':identities.append(payload.get('id'))
        if event.get('type')=='response_item' and payload.get('type') in ('custom_tool_call','custom_tool_call_output','function_call','function_call_output'):
            records.append({'type':payload['type'],'call_id':payload.get('call_id'),'name':payload.get('name'),
                            'start':offset,'end':offset+len(line),'line_sha256':hashlib.sha256(line).hexdigest()})
        offset+=len(line)
    if identities!=[thread_id]:raise ValueError('Raw history thread binding mismatch')
    calls={r['call_id'] for r in records if r['type'] in ('custom_tool_call','function_call')}
    outputs={r['call_id'] for r in records if r['type'].endswith('_output')}
    if None in calls|outputs:raise ValueError('Unbound tool record')
    result={'thread_id':thread_id,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'calls':len(calls),
            'outputs':len(outputs),'unmatched_calls':sorted(calls-outputs),'orphan_outputs':sorted(outputs-calls),
            'records':records,'scope':'Raw response tool records; nested operations require exact output inspection',
            'logical_capture_read_bytes':len(raw),'logical_capture_write_bytes':len(raw)}
    # Validate everything before publishing; existing evidence must not be replaced.
    out.mkdir(parents=True,exist_ok=True)
    with (out/'raw-rollout.jsonl').open('xb') as stream:stream.write(raw)
    with (out/'raw-tool-index.json').open('x') as stream:json.dump(result,stream,indent=2)
    return result
