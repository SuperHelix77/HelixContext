"""Temporary synthetic-directory-only interception test; fail open elsewhere."""
import json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent))
from post_tool import safe_transform
raw=sys.stdin.buffer.read();result={}
try:
    p=json.loads(raw)
    if Path(p.get('cwd','')).resolve()==(R/'sandbox').resolve():
        # Bounded rendezvous with caller-owned command-completion metadata.
        deadline=time.monotonic()+0.2
        while True:
            result=safe_transform(raw,R/'sandbox/bridge-archive',bridge_root=R/'bridge-live')
            if result or time.monotonic()>=deadline:break
            time.sleep(.005)
except Exception:pass
print(json.dumps(result))
