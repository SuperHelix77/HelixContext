"""Installed CLI serialization probe: loopback provider, isolated home, no model."""
import hashlib,json,os,subprocess,sys,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import tiktoken
CLI='/Applications/ChatGPT.app/Contents/Resources/codex'
MARKER='Helix serialization probe HXB_WIRE_20260909. Preserve ordinary task behavior.\n'
def run(root,out):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);home=root/'isolated-home';home.mkdir();cwd=root/'workspace';cwd.mkdir();marker=root/'marker.md';marker.write_text(MARKER)
 catalog=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-luna-prompt-diagnostic-v1-20260909/catalog.json');(root/'catalog.json').write_bytes(catalog.read_bytes())
 captures=[]
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
   captures.append({'path':self.path,'body':json.loads(raw),'authorization_header_present':'Authorization' in self.headers,'lite_header':self.headers.get('X-OpenAI-Internal-Codex-Responses-Lite'),'body_sha256':hashlib.sha256(raw).hexdigest()})
   self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(b'{"error":{"message":"Intentional loopback serialization capture; no inference","type":"invalid_request_error"}}')
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
 env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('API_KEY','TOKEN','SECRET','PASSWORD'))};env['CODEX_HOME']=str(home)
 enc=tiktoken.get_encoding('o200k_base');result={'classification':'Loopback custom-provider serialization; no hosted model execution','model_calls':0,'global_config_modified':False,'rows':[]}
 try:
  for model in ('gpt-5.6-sol','gpt-5.6-luna','gpt-6-astra'):
   for arm in ('default','override'):
    start=len(captures);args=[CLI,'exec','--skip-git-repo-check','--ephemeral','--json','-s','read-only','-m',model]
    configs={'model_provider':'capture','model_providers.capture.name':'Local serialization capture','model_providers.capture.base_url':f'http://127.0.0.1:{server.server_port}/v1','model_providers.capture.wire_api':'responses','model_providers.capture.requires_openai_auth':False,'model_providers.capture.request_max_retries':0,'model_providers.capture.stream_max_retries':0,'model_catalog_json':str(root/'catalog.json'),'model_reasoning_effort':'high'}
    if arm=='override':configs['model_instructions_file']=str(marker)
    for k,v in configs.items():args+=['-c',k+'='+json.dumps(v)]
    args+=['Serialization-only request; no response is expected.']
    p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=30)
    name=model+'-'+arm;(root/(name+'.stderr')).write_text(p.stderr);batch=captures[start:];(root/(name+'.capture.json')).write_text(json.dumps(batch,indent=2))
    if not batch:raise ValueError('No request captured: '+name+' '+p.stderr[-1000:])
    assert all(not x['authorization_header_present'] for x in batch),'unexpected auth header'
    b=batch[0]['body'];texts=[c.get('text','') for item in b.get('input',[]) for c in item.get('content',[]) if isinstance(c,dict)]
    instructions=b.get('instructions','');texts=[t for t in texts if isinstance(t,str)]
    result['rows'].append({'model':model,'arm':arm,'process_exit':p.returncode,'captured_requests':len(batch),'lite_header':batch[0]['lite_header'],'top_level_instruction_bytes':len(instructions.encode()),'top_level_instruction_proxy':len(enc.encode(instructions)),'marker_in_top_level':MARKER.strip() in instructions,'marker_in_input':any(MARKER.strip() in t for t in texts),'input_text_proxy':sum(len(enc.encode(t)) for t in texts),'tool_count':len(b.get('tools',[])) if b.get('tools') is not None else None,'input_item_types':[i.get('type') for i in b.get('input',[])],'request_sha256':batch[0]['body_sha256']});print(json.dumps(result['rows'][-1]),flush=True)
 finally:server.shutdown();server.server_close();worker.join()
 result['limits']=['Custom no-auth loopback provider, not hosted authenticated service.','Intentional400response confirms serialization only; no generated response, token receipt or capability test.','Hosted service-injected instructions cannot be observed by this mock.','No credentials or global config used; raw request bodies remain local.']
 Path(out).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run(*sys.argv[1:])
