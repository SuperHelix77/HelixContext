"""Frozen reasoning-only review pair using the existing Helix native session."""
from pathlib import Path
import difflib, hashlib, importlib.util, json, subprocess, sys, time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path[:0]=[str(REPO/'engine/output')]
import effort_session as native
import caller_memory_receipt as memory
import caller_registration
MODEL='gpt-6-astra';EFFORT='xhigh'
CLI=Path(native.RPC.__init__.__globals__['CLI'])
CONFIG=Path.home()/'.codex/config.toml';AGENTS=Path.home()/'.codex/AGENTS.md'
SKILL=Path.home()/'.codex/skills/helixcontext/SKILL.md'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def protected(cwd):return {str(p.relative_to(cwd)):sha(p.read_bytes()) for p in cwd.rglob('*') if p.is_file() and '.helix' not in p.parts and '__pycache__' not in p.parts}
def verify(m):
    for name,digest in m['bindings'].items():
        if sha(Path(name).read_bytes())!=digest:raise ValueError('Binding changed: '+name)

def prepare(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);started=time.perf_counter()
    task=(HERE/'TASK.md').read_text();style=(HERE/'STYLE.txt').read_text()
    catalog=subprocess.check_output([str(CLI),'debug','models']);(root/'catalog.json').write_bytes(catalog)
    model=next(r for r in json.loads(catalog)['models'] if r['slug']==MODEL)
    source={p.name:p.read_bytes() for p in (HERE/'fixture').glob('*.py')}
    expected=load(HERE/'OFFLINE_FIXTURE.json')
    if expected['public_exit']!=0 or expected['witnesses']['proposal_r.py']!={k:True for k in expected['witnesses']['proposal_r.py']}:raise ValueError('Offline gate failed')
    receipt={'schema':'helix.regression-snapshot.v1','source_hashes':{n:sha(raw) for n,raw in source.items()},'command':expected['public_argv'],'exit_status':0,'passed_tests':8,'exact_output_sha256':expected['public_stdout_sha256'],'authority':'Execution on the identical source snapshot only; coverage and semantic correctness are not established.'}
    source_view='\n'.join('FILE '+n+'\n'+b.decode() for n,b in source.items())
    common=(task+'\nCaller checked these current source hashes and executed the supplied tests against the identical source snapshot before inference. Original files and normal tools remain available.\n'+json.dumps(receipt,sort_keys=True)+'\nExact source:\n'+source_view+'\n')
    order=['on','off'] if int(sha(task.encode())[-1],16)%2 else ['off','on']
    paths=[Path(__file__),HERE/'PREREG.md',HERE/'TASK.md',HERE/'STYLE.txt',HERE/'OFFLINE_FIXTURE.json',HERE/'hidden_check.py',CONFIG,AGENTS,SKILL,CLI,native.HELPER,Path(native.__file__),Path(memory.__file__),Path(caller_registration.__file__),REPO/'engine/output/app_server_native.py',REPO/'engine/output/raw_receipts.py',REPO/'engine/output/config_bound_session.py',root/'catalog.json']+list((HERE/'fixture').glob('*.py'))
    m={'schema':'helix.reasoning-notation.v1','model':MODEL,'effort':EFFORT,'order':order,'base_sha256':sha(model['base_instructions'].encode()),'style_sha256':sha(style.encode()),'source_hashes':receipt['source_hashes'],'bindings':{}}
    rendered={}
    for arm in order:
        folder=root/arm;folder.mkdir();cwd=folder/'work';cwd.mkdir()
        files={**source,'TASK.md':task.encode(),'AGENTS.md':memory.LOCAL_RULE.encode(),'.agents/skills/helixcontext/SKILL.md':SKILL.read_bytes()}
        for n,raw in files.items():
            p=cwd/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        prompt=common+(style if arm=='on' else '')
        memory.prepare(cwd,prompt,'current scoped cache API review',folder/'memory')
        prompt=memory.attach(cwd,prompt,folder/'memory',sha((folder/'memory/receipt.json').read_bytes()))
        (folder/'prompt.txt').write_text(prompt);save(folder/'protected.json',protected(cwd))
        # No inference: installed client renders its prompt inputs.
        rendered[arm]=subprocess.check_output([str(CLI),'debug','prompt-input','-c','model="'+MODEL+'"','-c','model_reasoning_effort="xhigh"','-c','skills.max_context_tokens=512',prompt],cwd=cwd)
        (folder/'debug-prompt.json').write_bytes(rendered[arm])
        paths += [cwd/n for n in files]+list((folder/'memory').iterdir())+[folder/'prompt.txt',folder/'protected.json',folder/'debug-prompt.json']
    normalized={}
    for arm,raw in rendered.items():
        obj=json.loads(raw)
        def norm(x):
            if isinstance(x,str):return x.replace(str(root/arm/'work'),'<TASK_CWD>').replace(style,'')
            if isinstance(x,list):return [norm(v) for v in x]
            if isinstance(x,dict):
                result={k:norm(v) for k,v in x.items()}
                if x.get('type')=='message':
                    if 'id' in result:result['id']='<FRESH_MESSAGE_ID>'
                    meta=result.get('internal_chat_message_metadata_passthrough',{})
                    if 'create_time' in meta:meta['create_time']='<RENDER_TIME>'
                return result
            return x
        normalized[arm]=norm(obj)
    match=normalized['on']==normalized['off']
    save(root/'debug-comparison.json',{'equal_after_documented_normalization':match,'ignored_transport_metadata':['message.id','message.internal_chat_message_metadata_passthrough.create_time'],'native_calls':0,'limits':'CLI-rendered input, not hosted server context or native skill injection.'})
    if not match:
        (root/'debug-diff.txt').write_text(''.join(difflib.unified_diff(json.dumps(normalized['off'],indent=2).splitlines(True),json.dumps(normalized['on'],indent=2).splitlines(True))))
        raise ValueError('Offline rendered prompt has unexplained differences')
    # Validate the existing authenticated native setup, but never start a turn.
    with native.Session(MODEL,root/'off/work',root/'native-preflight',root/'off/work/.agents/skills/helixcontext/SKILL.md',effort=EFFORT) as session:
        assert session.turns==[]
    if session.failed:raise ValueError('Native setup gate failed')
    m['preparation_seconds']=time.perf_counter()-started
    m['bindings']={str(p.resolve()):sha(p.read_bytes()) for p in paths}
    save(root/'manifest.json',m)
    print(json.dumps({'prepared':str(root),'order':order,'native_calls':0,'equal_debug_inputs':match,'manifest_sha256':sha((root/'manifest.json').read_bytes())}),flush=True)

def run(root):
    root=Path(root).resolve();m=load(root/'manifest.json');verify(m)
    path=root/'results.json'
    if path.exists():raise ValueError('No rerun or automatic retry')
    result={'state':'RUNNING','manifest_sha256':sha((root/'manifest.json').read_bytes()),'rows':[]};save(path,result)
    try:
        for arm in m['order']:
            verify(m);folder=root/arm;cwd=folder/'work';before=load(folder/'protected.json')
            row={'arm':arm,'state':'RUNNING'};result['rows'].append(row);save(path,result)
            with native.Session(MODEL,cwd,folder/'native',cwd/'.agents/skills/helixcontext/SKILL.md',effort=EFFORT) as session:
                verify(m)
                answer,turn=session.turn(caller_registration.attach(session,(folder/'prompt.txt').read_text()))
                row.update(answer=answer,turn=turn,usage=dict(session.total));save(path,result)
            if session.failed:raise ValueError('Native audit failed')
            verify(m)
            current=protected(cwd)
            if any(current.get(k)!=v for k,v in before.items()):raise ValueError('Protected input changed')
            row.update(state='AWAITING_SEMANTIC_AUDIT',extra_files=sorted(set(current)-set(before)),elapsed_seconds=time.perf_counter()-session.started)
            save(path,result);print(json.dumps({k:row[k] for k in ['arm','state','usage']}),flush=True)
        result['state']='AWAITING_AUDIT';save(path,result)
    except BaseException as e:
        result.update(state='STOPPED_PENDING_AUDIT',error=repr(e));save(path,result);raise

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]](sys.argv[2])
