"""Read-only observer of one task's hook inputs; never replaces native output."""
import json,sys,uuid
from pathlib import Path
root=Path(__file__).resolve().parent/'sandbox'
raw=sys.stdin.buffer.read()
try:
    payload=json.loads(raw)
    if Path(payload.get('cwd','')).resolve()==root.resolve() and payload.get('hook_event_name')=='PostToolUse':
        archive=root/'hook-inputs';archive.mkdir(exist_ok=True)
        (archive/(uuid.uuid4().hex+'.json')).write_bytes(raw)
except Exception:pass
print('{}')
