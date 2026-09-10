"""Zero-inference, no-credential probe of user-owned AGENTS continuity isolation.

Two otherwise identical isolated CLI homes differ only in the Helix-specific
sections copied from the user's AGENTS file. Does not change the real home/config,
run the activation helper, or establish authenticated app-server equivalence.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

CLI=Path('/Applications/ChatGPT.app/Contents/Resources/codex')
GLOBAL=Path('/Users/mert/.codex/AGENTS.md')
CONFIG=Path('/Users/mert/.codex/config.toml')
CATALOG=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-luna-prompt-diagnostic-v1-20260909/catalog.json')
MARKER='runtime-b09051d7f65fa98b.py activate'


def digest(raw):return hashlib.sha256(raw).hexdigest()


def run(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    global_raw=GLOBAL.read_bytes();config_hash=digest(CONFIG.read_bytes())
    text=global_raw.decode();assert text.count('\n# Continuity\n')==1
    memory_only=text.split('\n# Continuity\n',1)[0]+'\n'
    assert '# Memory' in memory_only and 'recall --query' in memory_only and MARKER not in memory_only
    (root/'catalog.json').write_bytes(CATALOG.read_bytes())
    workspace=root/'workspace';workspace.mkdir();captures=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            raw=self.rfile.read(int(self.headers['Content-Length']))
            captures.append({'body':json.loads(raw),'sha256':digest(raw),
                             'authorization_present':'Authorization' in self.headers})
            self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers()
            self.wfile.write(b'{"error":{"type":"invalid_request_error","message":"Intentional local capture; no inference"}}')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start();rows=[]
    try:
        for arm,agents in [('shared_helix_instructions',text),('memory_only_baseline',memory_only)]:
            isolated=root/arm;isolated.mkdir();(isolated/'AGENTS.md').write_text(agents)
            env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ('API_KEY','TOKEN','SECRET','PASSWORD'))}
            env['CODEX_HOME']=str(isolated) # Process-local intended configuration home, never the production home.
            configs={'model_provider':'capture','model_providers.capture.name':'Local evidence capture',
                'model_providers.capture.base_url':f'http://127.0.0.1:{server.server_port}/v1',
                'model_providers.capture.wire_api':'responses','model_providers.capture.requires_openai_auth':False,
                'model_providers.capture.request_max_retries':0,'model_providers.capture.stream_max_retries':0,
                'model_catalog_json':str(root/'catalog.json'),'model_reasoning_effort':'high'}
            args=[str(CLI),'exec','--skip-git-repo-check','--ephemeral','--json','-s','read-only','-m','gpt-5.6-sol']
            for k,v in configs.items():args+=['-c',k+'='+json.dumps(v)]
            args+=['Serialization-only task. No generated answer or execution expected.']
            start=len(captures);p=subprocess.run(args,cwd=workspace,env=env,capture_output=True,timeout=30)
            batch=captures[start:];assert len(batch)==1 and not batch[0]['authorization_present']
            (root/(arm+'.capture.json')).write_text(json.dumps(batch,indent=2)+'\n')
            (root/(arm+'.stderr')).write_bytes(p.stderr)
            body=batch[0]['body'];texts=[c.get('text','') for item in body.get('input',[]) for c in item.get('content',[]) if isinstance(c,dict)]
            present=any(MARKER in s for s in texts)
            assert present==(arm=='shared_helix_instructions')
            assert any('recall --query' in s for s in texts) # Required ordinary memory instruction retained.
            rows.append({'arm':arm,'process_exit':p.returncode,'captured_requests':1,
                'known_user_owned_activation_instruction_present':present,'ordinary_memory_instruction_present':True,
                'agents_bytes':len(agents.encode()),'input_text_bytes':sum(len(s.encode()) for s in texts),
                'tool_count':len(body.get('tools') or []),'request_sha256':batch[0]['sha256'],
                'authorization_header_present':False,'model_calls':0})
    finally:server.shutdown();server.server_close();worker.join()
    assert GLOBAL.read_bytes()==global_raw and digest(CONFIG.read_bytes())==config_hash
    result={'classification':'Offline client instruction-isolation evidence; no native economics or capability inference',
        'rows':rows,'native_model_calls':0,'global_agents_sha256':digest(global_raw),
        'cli_sha256':digest(CLI.read_bytes()),'catalog_sha256':digest(CATALOG.read_bytes()),
        'production_config_and_agents_unchanged':True,
        'limits':['Synthetic no-auth loopback CLI; not authenticated app-server or desktop integration.',
                  'Other skill catalogs, tools, hooks, provider context and effective config require prospective binding.',
                  'No served model response, native token saving, cache effect or semantic parity measured.']}
    (root/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (Path(__file__).parent/'CONTROL_BOUNDARY_OFFLINE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':run(sys.argv[1])
