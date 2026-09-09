"""User-authorized temporary observer registration, exact trust and cleanup."""
import hashlib,json,time,tomllib
from pathlib import Path
from rpc_client import Client
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from metadata_bridge import Bridge
R=Path(__file__).resolve().parent
bridge=Bridge(R/'bridge-live')
script=R/'bridge_scoped.py';expected='a26e0a45984cf3acbcfd35cdd287f1cc4e65c218505a2d5baac561b3b0bb2e6f'
assert hashlib.sha256(script.read_bytes()).hexdigest()==expected
config=Path.home()/'.codex/config.toml';original=config.read_bytes()
(R/'config-before-bridge-probe.private.toml').write_bytes(original)
marker='# HELIX TEMPORARY OBSERVER 20260909'
assert marker not in original.decode()
command='python3 '+str(script)
block='\n'+marker+'\n[[hooks.PostToolUse]]\nmatcher = "^Bash$"\n[[hooks.PostToolUse.hooks]]\ntype = "command"\ncommand = '+json.dumps(command)+'\ntimeout = 2\n# END HELIX TEMPORARY OBSERVER\n'
trustblock='';client=None;result={'observer_sha256':expected,'user_authorized':True,'native_run_started':False};log=None
try:
    text=original.decode()+block;tomllib.loads(text)
    assert config.read_bytes()==original,'Concurrent configuration edit'
    config.write_text(text)
    client=Client()
    def listed():
        return [h for e in client.call('hooks/list',{'cwds':[str(R/'sandbox')]})['data'] for h in e['hooks'] if h.get('command')==command]
    found=listed();assert len(found)==1,found
    hook=found[0];assert hook['sourcePath']==str(config) and not hook['isManaged']
    assert hook['key'] not in tomllib.loads(config.read_text()).get('hooks',{}).get('state',{})
    trustblock='\n[hooks.state.'+json.dumps(hook['key'])+']\ntrusted_hash = '+json.dumps(hook['currentHash'])+'\n'
    current=config.read_text();tomllib.loads(current+trustblock);config.write_text(current+trustblock)
    trusted=listed();assert len(trusted)==1 and trusted[0]['currentHash']==hook['currentHash'] and trusted[0]['trustStatus']=='trusted',trusted
    result['trusted_definition_hash']=hook['currentHash'];print('Temporary observer registered and exact definition trusted.',flush=True)
    assert hashlib.sha256(script.read_bytes()).hexdigest()==expected
    # Restart so thread creation has the same freshly reviewed configuration.
    client.close();client=Client();assert listed()[0]['trustStatus']=='trusted'
    prior=set((R/'sandbox/hook-inputs').glob('*.json'))
    log=(R/'bridge-probe-events.private.jsonl').open('w')
    t=client.call('thread/start',{'model':'gpt-5.6-sol','cwd':str(R/'sandbox'),'ephemeral':True,'approvalPolicy':'never','sandbox':'workspace-write'})
    client.call('turn/start',{'threadId':t['thread']['id'],'effort':'high','input':[{'type':'text','text':'Synthetic tool-result compatibility probe. Run python3 bridge_probe.py twice as two separate shell tool calls. Do not combine, retry, or inspect its source. Nonzero status is expected fixture behavior. Then return only JSON with exit_codes (two observed integers) and schemas (the schema string from each tool response if present, otherwise null). Use the actual tool results.'}]})
    result['native_run_started']=True;events=[];start=time.time()
    while time.time()-start<180:
        try:e=client.read(20)
        except TimeoutError:continue
        bridge.publish(e)
        log.write(json.dumps(e)+'\n');log.flush();events.append(e)
        if e.get('method')=='turn/completed':break
    else:raise TimeoutError('Native observer deadline')
    captured=set((R/'sandbox/hook-inputs').glob('*.json'))-prior
    shapes=[]
    for path in captured:
        p=json.loads(path.read_text());r=p.get('tool_response')
        shapes.append({'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'type':type(r).__name__,'keys':list(r) if isinstance(r,dict) else None,'response_prefix':str(r)[:250]})
    answers=[e['params']['item'].get('text','') for e in events if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='agentMessage']
    result['bridge_publisher_io']=dict(bridge.metrics)
    result['captured_files']=[str(path) for path in captured]
    result.update(captured_events=len(captured),response_shapes=shapes,final_done=bool(answers and answers[-1].strip()=='DONE'),usage_events=[e['params'] for e in events if e.get('method')=='thread/tokenUsage/updated'],scope='Native exit-status observer probe; synthetic native metadata-bridge replacement experiment')
    print('Native observer captured',len(captured),'event(s).',flush=True)
except Exception as exc:
    result['error']=str(exc);raise
finally:
    if log:log.close()
    if client:client.close()
    current=config.read_text()
    for own in (trustblock,block):
        if own:
            assert current.count(own)==1,'Temporary registration changed concurrently; inspect cleanup'
            current=current.replace(own,'',1)
    import re
    before_obj=tomllib.loads(original.decode());now_obj=tomllib.loads(current);project=str(R/'sandbox')
    if project not in before_obj.get('projects',{}) and now_obj.get('projects',{}).get(project)=={'trust_level':'trusted'}:
        header='[projects.'+json.dumps(project)+']'
        current,n=re.subn(r'(?m)^'+re.escape(header)+r'\ntrust_level = "trusted"\n?','',current);assert n==1
    tomllib.loads(current);config.write_text(current)
    result['configuration_values_restored']=tomllib.loads(current)==before_obj
    result['configuration_restored_exactly']=config.read_bytes()==original
    check=Client()
    try:result['temporary_observer_removed']=not any(h.get('command')==command for e in check.call('hooks/list',{'cwds':[str(R/'sandbox')]})['data'] for h in e['hooks'])
    finally:check.close()
    (R/'BRIDGE_PROBE_RESULT.private.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('usage_events','response_shapes')},indent=2),flush=True)
