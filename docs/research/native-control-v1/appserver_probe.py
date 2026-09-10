"""Installed app-server isolation and tool lifecycle probe; no hosted inference.

The loopback server scripts a harmless shell read, a bound caller callback and a
synthetic completion. Its fabricated usage is explicitly NOT economic evidence.
Real configuration/credentials are never copied, changed or sent to the mock.
"""
import hashlib
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'engine/output'))
from app_server_native import RPC, CLI
from dynamic_tool_rpc import rpc_type

GLOBAL=Path('/Users/mert/.codex/AGENTS.md')
CONFIG=Path('/Users/mert/.codex/config.toml')
CATALOG=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-luna-prompt-diagnostic-v1-20260909/catalog.json')
ACTIVATION='runtime-b09051d7f65fa98b.py activate'
SPEC={'type':'function','name':'boundary_probe','description':'Read the caller-bound synthetic source; diagnostic only.',
      'inputSchema':{'type':'object','properties':{'id':{'type':'string'}},'required':['id'],'additionalProperties':False}}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def run(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);os.chmod(root,0o700)
    originals={GLOBAL:digest(GLOBAL.read_bytes()),CONFIG:digest(CONFIG.read_bytes())}
    save(root/'production-bindings.json',{str(p):h for p,h in originals.items()})
    text=GLOBAL.read_text();assert text.count('\n# Continuity\n')==1
    ordinary=text.split('\n# Continuity\n',1)[0]+'\n'
    (root/'catalog.json').write_bytes(CATALOG.read_bytes())
    source=b'HELIX_BOUNDARY_EXACT_SOURCE\n';captures=[];active={};rows=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            raw=self.rfile.read(int(self.headers['Content-Length']));body=json.loads(raw)
            assert 'Authorization' not in self.headers
            batch=active['captures'];batch.append({'body':body,'sha256':digest(raw),'auth_present':False})
            index=len(batch)
            if index==1:
                code='text(await tools.exec_command({cmd:"printf HELIX_NATIVE_TOOL_OK",login:false,max_output_tokens:100}));'
            elif index==2:
                code='text(await tools.boundary_probe({id:"source"}));'
            else:code=None
            if code:
                item={'id':'tool_'+str(index),'type':'custom_tool_call','call_id':'call_'+str(index),
                      'namespace':'functions','name':'exec','input':code}
            else:
                item={'id':'message_final','type':'message','role':'assistant','status':'completed',
                      'content':[{'type':'output_text','text':'SYNTHETIC_BOUNDARY_COMPLETE','annotations':[]}]}
            response={'id':'response_'+str(index),'object':'response','status':'completed','output':[item],
                      'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2,
                      'input_tokens_details':{'cached_tokens':0},'output_tokens_details':{'reasoning_tokens':0}}}
            events=[{'type':'response.created','response':{**response,'status':'in_progress','output':[]}},
                    {'type':'response.output_item.done','output_index':0,'item':item},
                    {'type':'response.completed','response':response}]
            packet=''.join('event: '+e['type']+'\ndata: '+json.dumps(e)+'\n\n' for e in events).encode()
            self.send_response(200);self.send_header('Content-Type','text/event-stream')
            self.send_header('Content-Length',str(len(packet)));self.end_headers();self.wfile.write(packet)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:
        for arm,agents,attach in [('shared_continuity',text,False),('ordinary_memory',ordinary,False),('helix_attached',ordinary,True)]:
            folder=root/arm;folder.mkdir();home=folder/'home';home.mkdir();cwd=folder/'work';cwd.mkdir();out=folder/'rpc';out.mkdir()
            subprocess.run(['git','init','-q'],cwd=cwd,check=True)
            git_root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=cwd,text=True).strip()).resolve()
            assert git_root==cwd.resolve() and not (cwd/'.codex').exists()
            (home/'AGENTS.md').write_text(agents);(cwd/'source.dat').write_bytes(source)
            skill=cwd/'.agents/skills/helixcontext/SKILL.md'
            if attach:skill.parent.mkdir(parents=True);skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
            cfg={'model_provider':'capture','model_providers.capture.name':'Offline boundary capture',
                 'model_providers.capture.base_url':f'http://127.0.0.1:{server.server_port}/v1',
                 'model_providers.capture.wire_api':'responses','model_providers.capture.requires_openai_auth':False,
                 'model_providers.capture.request_max_retries':0,'model_providers.capture.stream_max_retries':0,
                 'model_catalog_json':str(root/'catalog.json')}
            # Explicit caller-owned trust for this synthetic Git root. Unexpected
            # parent registration or any later config rewrite still fails the guard.
            cfg['projects.'+json.dumps(str(cwd.resolve()))+'.trust_level']='trusted'
            config='\n'.join(k+'='+json.dumps(v) for k,v in cfg.items())+'\n'
            (home/'config.toml').write_text(config)
            env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('API_KEY','TOKEN','SECRET','PASSWORD'))}
            env['CODEX_HOME']=str(home) # Child-only intended home; no process-global environment mutation.
            callback=[]
            def handle(params):
                assert params['arguments']=={'id':'source'} and (cwd/'source.dat').read_bytes()==source
                callback.append(params)
                return {'success':True,'contentItems':[{'type':'inputText','text':json.dumps({
                    'marker':'HELIX_CALLER_TOOL_OK','sha256':digest(source),'bytes':len(source)})}]}
            Base=rpc_type([SPEC],handle)
            class ScopedRPC(Base):
                def __init__(self):
                    # Same installed RPC protocol; explicit child env is the only launch extension.
                    self.out=out;self.raw=(out/'native-events.jsonl').open('wb');self.requests=(out/'requests.jsonl').open('wb');self.stderr=(out/'stderr.txt').open('wb')
                    self.p=subprocess.Popen([CLI,'app-server','--stdio','-c','model="gpt-5.6-sol"',
                        '-c','model_reasoning_effort="high"','-c','skills.max_context_tokens=512'],
                        cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,bufsize=0,start_new_session=True)
                    self.selector=selectors.DefaultSelector();self.selector.register(self.p.stdout,selectors.EVENT_READ)
                    self.buffer=b'';self.next_id=0;self.events=[];self.deadline=time.monotonic()+45
                    self.bound_thread=None;self.active_turn=None;self.delivered={}
            active['captures']=[];rpc=ScopedRPC()
            try:
                rpc.call('initialize',{'clientInfo':{'name':'helix-offline-boundary','version':'1'},'capabilities':{'experimentalApi':True}})
                rpc.send({'method':'initialized'})
                hooks=rpc.call('hooks/list',{'cwds':[str(cwd)]});save(folder/'hooks.json',hooks)
                assert not any(row['hooks'] for row in hooks['data'])
                skills=rpc.call('skills/list',{'cwds':[str(cwd)],'forceReload':True});save(folder/'skills.json',skills)
                declared=[s for row in skills['data'] for s in row['skills'] if s['name']=='helixcontext' and s['enabled']]
                assert len(declared)==int(attach)
                thread_params={'model':'gpt-5.6-sol','modelProvider':'capture','cwd':str(cwd),'approvalPolicy':'never',
                    'sandbox':'workspace-write','ephemeral':False,'config':{'model_reasoning_effort':'high','skills.max_context_tokens':512}}
                if attach:thread_params['config']['model_instructions_file']=str(REPO/'engine/profiles/sol-coding-transfer-v1/base.md')
                started=rpc.call('thread/start',thread_params);save(folder/'thread-start.json',started)
                assert started['model']=='gpt-5.6-sol' and started['reasoningEffort']=='high'
                assert started['approvalPolicy']=='never' and started['modelProvider']=='capture'
                inputs=[{'type':'text','text':'Offline transport probe only. All output and usage are synthetic. Read-only diagnostic operations authorized; no real task.'}]
                if attach:inputs.append({'type':'skill','name':'helixcontext','path':str(skill)})
                turn=rpc.call('turn/start',{'threadId':started['thread']['id'],'model':'gpt-5.6-sol','effort':'high','input':inputs})
                while not any(e.get('method')=='turn/completed' for e in rpc.events):rpc.read()
                done=next(e['params']['turn'] for e in rpc.events if e.get('method')=='turn/completed')
                assert done['status']=='completed'
            finally:rpc.close()
            batch=active['captures'];save(folder/'captures.private.json',batch);assert len(batch)==3 and len(callback)==1
            first=batch[0]['body'];texts=[c.get('text','') for i in first.get('input',[]) for c in i.get('content',[]) if isinstance(c,dict)]
            assert any(ACTIVATION in t for t in texts)==(arm=='shared_continuity')
            assert any('recall --query' in t for t in texts)
            if attach:assert any('HELIX: Hierarchical Evidence Loading' in t for t in texts)
            items=[e['params']['item'] for e in rpc.events if e.get('method')=='item/completed']
            commands=[i for i in items if i.get('type')=='commandExecution']
            assert len(commands)==1 and commands[0]['exitCode']==0 and commands[0]['aggregatedOutput']=='HELIX_NATIVE_TOOL_OK'
            tools=[i for i in items if i.get('type')=='dynamicToolCall']
            assert len(tools)==1 and tools[0]['success'] and tools[0]['tool']=='boundary_probe'
            assert any(i.get('type')=='agentMessage' and i.get('text')=='SYNTHETIC_BOUNDARY_COMPLETE' for i in items)
            assert (home/'config.toml').read_text()==config and (cwd/'source.dat').read_bytes()==source
            rows.append({'arm':arm,'global_activation_in_input':arm=='shared_continuity','memory_instruction_retained':True,
                'skill_attached':attach,'skill_sha256':digest(skill.read_bytes()) if attach else None,
                'declared_hooks':0,'model':'gpt-5.6-sol','effort':'high','local_provider_requests':len(batch),
                'ordinary_shell_commands':1,'caller_callbacks':1,'synthetic_final_item':True,
                'input_text_bytes':sum(len(t.encode()) for t in texts),'synthetic_usage_not_economic_evidence':True,
                'native_model_calls':0,'native_events_sha256':digest((out/'native-events.jsonl').read_bytes()),
                'config_sha256':digest(config.encode())})
            save(root/'progress.json',{'rows':rows,'hosted_model_calls':0});print(json.dumps(rows[-1]),flush=True)
    finally:server.shutdown();server.server_close();worker.join()
    assert all(digest(p.read_bytes())==h for p,h in originals.items())
    result={'classification':'Offline installed app-server lifecycle and instruction-boundary evidence, not model parity',
            'rows':rows,'hosted_model_calls':0,'global_config_and_agents_unchanged':True,
            'cli_sha256':digest(Path(CLI).read_bytes()),'source_sha256':digest(Path(__file__).read_bytes()),
            'limits':['Loopback scripted responses and fake usage; not economic evidence or model-written answers.',
                      'One shell primitive and one callback do not certify every native tool or semantic capability.',
                      'Actual authenticated settings, skill/MCP catalogs, hooks and project trust still require separate binding.']}
    save(root/'result.json',result);save(HERE/'APPSERVER_OFFLINE.json',result)


if __name__=='__main__':run(sys.argv[1])
