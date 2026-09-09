"""Observable native trace anatomy; never reconstructs private reasoning."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'prototype'))
from native_usage import aggregate


def profile(path):
    raw=Path(path).read_bytes()
    events=[json.loads(line) for line in raw.splitlines() if line.strip()]
    usage=aggregate([e['usage'] for e in events if e.get('type')=='turn.completed'])
    completed=[e['item'] for e in events if e.get('type')=='item.completed']
    commands=[i for i in completed if i.get('type')=='command_execution']
    messages=[i for i in completed if i.get('type')=='agent_message']
    types={kind:sum(i.get('type')==kind for i in completed) for kind in sorted({i.get('type','unknown') for i in completed})}
    return {'schema':'helix.observable_trace.v1','events_sha256':hashlib.sha256(raw).hexdigest(),
        'native_usage':usage,'completed_item_types':types,
        'commands':len(commands),'command_text_bytes':sum(len(i.get('command','').encode()) for i in commands),
        'recorded_terminal_bytes':sum(len(i.get('aggregated_output','').encode()) for i in commands),
        'nonzero_command_exits':sum(i.get('exit_code') is not None and i['exit_code']!=0 for i in commands),
        'missing_command_exits':sum(i.get('exit_code') is None for i in commands),
        'message_text_bytes':sum(len(i.get('text','').encode()) for i in messages),
        'limitations':['Bytes are not native tokens or disjoint native output categories.',
            'Recorded terminal text may already be truncated; raw subprocess bytes may differ.',
            'File-change events need not contain generated patch text.',
            'No private reasoning contents or causal model psychology are inferred.',
            'Model/effort identity must be verified separately against the launch receipt.']}


if __name__=='__main__':
    print(json.dumps(profile(sys.argv[1]),indent=2))
