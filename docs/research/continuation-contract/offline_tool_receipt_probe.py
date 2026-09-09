"""Isolated loopback Responses stream: inspect native tool receipt coverage.

No credentials, production configuration or hosted model calls. The mock emits
one fixed harmless command; a later local request exposes its exact result.
"""
import json,os,subprocess,sys,threading,selectors,time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

CLI='/Applications/ChatGPT.app/Contents/Resources/codex'


def run(root,mode='discover',transport='cli'):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    home=root/'home';home.mkdir();work=root/'work';work.mkdir()
    catalog=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-luna-prompt-diagnostic-v1-20260909/catalog.json')
    (root/'catalog.json').write_bytes(catalog.read_bytes())
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append(body)
            (root/f'request-{len(requests)}.json').write_text(json.dumps(body,indent=2))
            item={'id':'msg_probe','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':'OFFLINE_PROBE_COMPLETE','annotations':[]}]}
            if mode!='discover' and len(requests)==1:
                command={'cmd':'printf HELIX_OFFLINE_COMMAND','login':False,'max_output_tokens':100}
                if mode=='missing_cwd':command['workdir']=str(root/'missing_directory')
                item={'id':'tool_probe','type':'custom_tool_call','call_id':'call_probe','namespace':'functions','name':'exec','input':'text(await tools.exec_command('+json.dumps(command)+'));'}
            response={'id':'resp_probe','object':'response','status':'completed','output':[item],'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2,'input_tokens_details':{'cached_tokens':0},'output_tokens_details':{'reasoning_tokens':0}}}
            events=[{'type':'response.created','response':{**response,'status':'in_progress','output':[]}}, {'type':'response.output_item.added','output_index':0,'item':{**item,'content':[]}}, {'type':'response.output_text.delta','item_id':'msg_probe','output_index':0,'content_index':0,'delta':'OFFLINE_PROBE_COMPLETE'}, {'type':'response.output_item.done','output_index':0,'item':item}, {'type':'response.completed','response':response}]
            if item['type']=='custom_tool_call':
                events=[{'type':'response.created','response':{**response,'status':'in_progress','output':[]}}, {'type':'response.output_item.done','output_index':0,'item':item}, {'type':'response.completed','response':response}]
            raw=''.join('event: '+e['type']+'\ndata: '+json.dumps(e)+'\n\n' for e in events).encode()
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    config={'model_provider':'capture','model_providers.capture.name':'Offline capture','model_providers.capture.base_url':f'http://127.0.0.1:{server.server_port}/v1','model_providers.capture.wire_api':'responses','model_providers.capture.requires_openai_auth':False,'model_providers.capture.request_max_retries':0,'model_providers.capture.stream_max_retries':0,'model_catalog_json':str(root/'catalog.json')}
    args=[CLI]
    for key,value in config.items():args+=['-c',key+'='+json.dumps(value)]
    args+=['exec','--json','--skip-git-repo-check','--sandbox','read-only','--model','gpt-5.6-luna','Offline synthetic receipt probe. No real user task.'] if transport=='cli' else ['app-server','--stdio']
    env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('TOKEN','SECRET','PASSWORD','API_KEY'))}
    env['CODEX_HOME']=str(home)
    try:
        with (root/'stdout.jsonl').open('wb') as out,(root/'stderr.txt').open('wb') as err:
            if transport=='cli':
                code=subprocess.run(args,cwd=work,env=env,stdout=out,stderr=err,timeout=45).returncode
            else:
                proc=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,bufsize=0)
                sel=selectors.DefaultSelector();sel.register(proc.stdout,selectors.EVENT_READ)
                buffer=b'';wire=[];serial=0;deadline=time.monotonic()+45
                def read():
                    nonlocal buffer
                    while b'\n' not in buffer:
                        if time.monotonic()>deadline:raise TimeoutError('offline RPC')
                        if not sel.select(.5):continue
                        chunk=os.read(proc.stdout.fileno(),65536)
                        if not chunk:raise RuntimeError('RPC closed')
                        buffer+=chunk
                    line,buffer=buffer.split(b'\n',1);out.write(line+b'\n');out.flush()
                    e=json.loads(line);wire.append(e);return e
                def send(e):proc.stdin.write((json.dumps(e)+'\n').encode());proc.stdin.flush()
                def call(method,params):
                    nonlocal serial
                    serial+=1;send({'id':serial,'method':method,'params':params})
                    while True:
                        e=read()
                        if e.get('id')==serial:
                            if 'error' in e:raise RuntimeError(e['error'])
                            return e['result']
                try:
                    call('initialize',{'clientInfo':{'name':'helix-offline','version':'1'},'capabilities':{'experimentalApi':True}});send({'method':'initialized'})
                    start=call('thread/start',{'model':'gpt-5.6-luna','modelProvider':'capture','cwd':str(work),'approvalPolicy':'never','sandbox':'read-only','ephemeral':transport!='persistent'})
                    (root/'thread-start.json').write_text(json.dumps(start,indent=2))
                    tid=start['thread']['id']
                    call('turn/start',{'threadId':tid,'input':[{'type':'text','text':'Offline synthetic receipt probe. No real user task.'}]})
                    while not any(e.get('method')=='turn/completed' for e in wire):read()
                    for method in ('thread/read','thread/items/list'):
                        try:value=call(method,{'threadId':tid,**({'includeTurns':True} if method=='thread/read' else {})})
                        except RuntimeError as exc:value={'inspection_error':str(exc)}
                        (root/(method.replace('/','-')+'.json')).write_text(json.dumps(value,indent=2))
                    code=0
                finally:
                    proc.terminate()
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
                    sel.close()
        result={'exit_code':code,'transport':transport,'mode':mode,'local_requests':len(requests),'hosted_model_calls':0,'synthetic_usage_not_economic_evidence':True,'production_config_changed':False}
    finally:server.shutdown();server.server_close();thread.join()
    (root/'result.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))


if __name__=='__main__':run(*sys.argv[1:])
