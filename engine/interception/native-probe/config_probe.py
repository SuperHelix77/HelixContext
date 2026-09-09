import json,hashlib
from pathlib import Path
from rpc_client import Client
R=Path(__file__).resolve().parent
command='python3 '+str(R/'observe.py')
config='hooks.PostToolUse=[{matcher="^Bash$",hooks=[{type="command",command='+json.dumps(command)+',timeout=2}]}]'
c=Client([config])
try:
    result=c.call('hooks/list',{'cwds':[str(R/'sandbox')]})
    found=[h for e in result['data'] for h in e['hooks'] if h.get('command')==command]
    (R/'config-observation.json').write_text(json.dumps(found,indent=2)+'\n')
    print(json.dumps(found,indent=2))
finally:c.close()
