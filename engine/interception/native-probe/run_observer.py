import json,time,hashlib
from pathlib import Path
from rpc_client import Client
R=Path(__file__).resolve().parent
hook=json.loads((R/'config-observation.json').read_text())[0]
command='python3 '+str(R/'observe.py')
assert hook['command']==command and hook['source']=='sessionFlags' and not hook['isManaged']
config='hooks.PostToolUse=[{matcher="^Bash$",hooks=[{type="command",command='+json.dumps(command)+',timeout=2}]}]'
trust='hooks.state.'+json.dumps(hook['key'])+'.trusted_hash='+json.dumps(hook['currentHash'])
c=Client([config,trust]);events=[];log=(R/'events.jsonl').open('w')
try:
    found=[h for e in c.call('hooks/list',{'cwds':[str(R/'sandbox')]})['data'] for h in e['hooks'] if h.get('command')==command]
    (R/'trust-observation.json').write_text(json.dumps(found,indent=2)+'\n');print(json.dumps(found,indent=2),flush=True)
    assert len(found)==1 and found[0]['currentHash']==hook['currentHash'] and found[0]['trustStatus']=='trusted'
    t=c.call('thread/start',{'model':'gpt-5.6-sol','cwd':str(R/'sandbox'),'ephemeral':True,'approvalPolicy':'never','sandbox':'workspace-write'})
    c.call('turn/start',{'threadId':t['thread']['id'],'effort':'high','input':[{'type':'text','text':'Synthetic hook-envelope probe. Run exactly this shell command once: python3 -c "print(\'line-0123456789\' * 1200); print(\'EXACT_END_000.050\')". Then reply DONE. No other work is needed.'}]})
    while True:
        e=c.read(30);events.append(e);log.write(json.dumps(e)+'\n');log.flush()
        if e.get('method')=='turn/completed':break
    captures=list((R/'sandbox/hook-inputs').glob('*.json'))
    result={'captured_events':len(captures),'observer_sha256':hashlib.sha256((R/'observe.py').read_bytes()).hexdigest(),'review':'Only reviewed task-scoped observe.py trusted through exact sessionFlags hash; no global config modification or blanket trust bypass. Observer only archives current synthetic task inputs and emits {}.','native_trace_sha256':hashlib.sha256((R/'events.jsonl').read_bytes()).hexdigest(),'response_shapes':[]}
    for file in captures:
        payload=json.loads(file.read_text());response=payload.get('tool_response')
        result['response_shapes'].append({'type':type(response).__name__,'keys':list(response) if isinstance(response,dict) else None,'prefix':str(response)[:500]})
    (R/'observation-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:log.close();c.close()
