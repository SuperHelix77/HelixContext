"""Account reported native usage segments without reading reasoning content."""
import hashlib
import json
from pathlib import Path
from app_server_native import usage


def segments(path,thread_id):
    raw=Path(path).read_bytes();rows=[];previous=None
    for line in raw.splitlines():
        event=json.loads(line)
        if event.get('method')!='thread/tokenUsage/updated' or event['params']['threadId']!=thread_id:continue
        total=usage(event)
        if previous==total:continue
        delta={k:v-(previous or {}).get(k,0) for k,v in total.items()}
        if any(v<0 for v in delta.values()):raise ValueError('Nonmonotonic usage')
        last=usage({'params':{'tokenUsage':{'total':event['params']['tokenUsage']['last']}}})
        if last!=delta:raise ValueError('Update does not identify a single complete reported segment')
        rows.append(delta);previous=total
    if not rows:raise ValueError('Missing native usage')
    return {'raw_sha256':hashlib.sha256(raw).hexdigest(),'reported_segments':rows,'total':previous,
            'scope':'Native reported usage segments, not a claim about hidden server calls or cognition.'}
