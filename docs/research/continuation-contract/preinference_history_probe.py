"""Disposable app-server history insertion probe; no turn/start or hosted calls."""
import json
import os
import selectors
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CLI='/Applications/ChatGPT.app/Contents/Resources/codex'


def run(root, trusted_home=None):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    home=root/'isolated-home';home.mkdir();workspace=root/'workspace';workspace.mkdir()
    if trusted_home is not None:
        home=Path(trusted_home).resolve()
        # Only this previously reviewed disposable home is permitted, not the
        # production home or an arbitrary credential-bearing profile.
        allowed=Path('/Users/mert/Documents/ChatGPT/Helix/research/pre-submit-hook-probe-20260910/isolated-home')
        if home!=allowed or (home/'auth.json').exists():raise ValueError('Not isolated hook home')
        workspace=Path('/tmp/helix-hook-review-workspace-20260910')
    catalog=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-luna-prompt-diagnostic-v1-20260909/catalog.json')
    (root/'catalog.json').write_bytes(catalog.read_bytes())
    hits=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length','0')))
            hits.append(self.path);self.send_response(400);self.end_headers()
            self.wfile.write(b'{"error":{"message":"offline probe; no model"}}')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    config={'model_provider':'capture','model_providers.capture.name':'Local no-model probe',
            'model_providers.capture.base_url':f'http://127.0.0.1:{server.server_port}/v1',
            'model_providers.capture.wire_api':'responses','model_providers.capture.requires_openai_auth':False,
            'model_providers.capture.request_max_retries':0,'model_providers.capture.stream_max_retries':0,
            'model_catalog_json':str(root/'catalog.json')}
    args=[CLI,'app-server','--stdio']
    for k,v in config.items(): args+=['-c',k+'='+json.dumps(v)]
    env={k:v for k,v in os.environ.items() if not any(s in k.upper() for s in ['TOKEN','SECRET','PASSWORD','API_KEY'])}
    env['CODEX_HOME']=str(home)
    stderr=(root/'stderr.txt').open('wb')
    proc=subprocess.Popen(args,cwd=workspace,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,bufsize=0)
    selector=selectors.DefaultSelector();selector.register(proc.stdout,selectors.EVENT_READ)
    wire=[];buffer=b'';rid=0
    def send(v): proc.stdin.write((json.dumps(v)+'\n').encode());proc.stdin.flush();wire.append({'sent':v})
    def call(method,params):
        nonlocal rid,buffer
        rid+=1;send({'id':rid,'method':method,'params':params});deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            if b'\n' not in buffer:
                if not selector.select(1):continue
                data=os.read(proc.stdout.fileno(),65536)
                if not data:raise RuntimeError('server closed')
                buffer+=data;continue
            line,buffer=buffer.split(b'\n',1);message=json.loads(line);wire.append({'received':message})
            if message.get('id')==rid:return message
        raise TimeoutError(method)
    result={'classification':'Offline isolated runtime probe','native_calls':0,'production_config_changed':False}
    try:
        result['initialize']=call('initialize',{'clientInfo':{'name':'helix_offline_probe','version':'1'},'capabilities':{'experimentalApi':True}})
        send({'method':'initialized','params':{}})
        start=call('thread/start',{'model':'gpt-5.6-luna','modelProvider':'capture','cwd':str(workspace),'approvalPolicy':'never','sandbox':'read-only'})
        result['start']=start
        thread=start['result']['thread']['id']
        if trusted_home is not None:
            result['blocked_start']=call('turn/start',{'threadId':thread,'input':[{'type':'text','text':'HELIX OFFLINE SYNTHETIC E01: no real user task.'}]})
            deadline=time.monotonic()+20
            while time.monotonic()<deadline:
                state=call('thread/read',{'threadId':thread,'includeTurns':True})
                if any(e.get('received',{}).get('method')=='turn/completed' for e in wire):break
                time.sleep(.05)
            else:raise TimeoutError('No authoritative turn/completed notification')
            result['blocked_read']=state
        item={'type':'message','role':'user','content':[{'type':'input_text','text':'HELIX ENGINE RECEIPT: synthetic completion E01; no model authored this record.'}]}
        result['inject']=call('thread/inject_items',{'threadId':thread,'items':[item]})
        result['read']=call('thread/read',{'threadId':thread,'includeTurns':True})
        result['items']=call('thread/items/list',{'threadId':thread,'limit':100})
        result['turns']=call('thread/turns/list',{'threadId':thread,'limit':100})
        result['duplicate_inject']=call('thread/inject_items',{'threadId':thread,'items':[item]})
        result['items_after_duplicate']=call('thread/items/list',{'threadId':thread,'limit':100})
        result['resume']=call('thread/resume',{'threadId':thread,'excludeTurns':True})
        result['items_after_resume']=call('thread/items/list',{'threadId':thread,'limit':100})
        result['provider_requests']=hits
        result['turn_start_sent']=any(x.get('sent',{}).get('method')=='turn/start' for x in wire)
    except Exception as exc:result['error']=repr(exc)
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        selector.close();stderr.close();server.shutdown();server.server_close();worker.join()
        (root/'wire.json').write_text(json.dumps(wire,indent=2)+'\n')
        (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':run(*sys.argv[1:])
