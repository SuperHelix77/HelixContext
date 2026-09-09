"""One adaptive coding candidate: source-only decision, caller checks/publication.

Reuses a known control; not a fresh pair or general parity evidence. Full raw
tool evidence retained. No output cap, weakened effort or tool restrictions.
"""
import ast,json,os,sys,time
from pathlib import Path
import luna_capability_pair as cap
from observed_session import Session
from caller_registration import attach
import observed_session,raw_receipts,caller_registration


def source(text):
    text=text.strip()
    if text.startswith('```python\n') and text.endswith('```'):text=text[len('```python\n'):-3]
    elif text.startswith('```\n') and text.endswith('```'):text=text[4:-3]
    if text.lstrip().startswith('{'):
        value=json.loads(text)
        if isinstance(value.get('semantic_obligations'),list) and value['semantic_obligations']:
            raise ValueError('Unresolved semantic obligations: '+json.dumps(value['semantic_obligations']))
        raise ValueError('Unexpected decision schema')
    ast.parse(text)
    return text.encode() + (b'' if text.endswith('\n') else b'\n')


def prepare(root,prior):
    root=Path(root).resolve();prior=Path(prior).resolve();root.mkdir(parents=True,exist_ok=False)
    spec=json.loads((prior/'coding-source.json').read_text());cap.kd.save(root/'coding-source.json',spec)
    cwd=root/'on';cwd.mkdir()
    for name,text in spec['files'].items():(cwd/name).write_text(text)
    skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True)
    skill.write_bytes((cap.kd.REPO/'skills/helixcontext/SKILL.md').read_bytes())
    prompt='Caller completed memory consultation; no recalled task facts. Caller owns benchmark bookkeeping. Work only in this task directory.\n'+spec['task']+'''
Caller execution: return only the complete replacement Python module. Caller stages these exact bytes, runs the existing unittest suite and independent allocation oracle, and publishes allocation.py only if checks pass and protected inputs are unchanged. Leave the original files unchanged for caller publication. Checks and publication are pending mechanics, not unresolved semantics. Caller reports actual results; do not claim tests ran before they do. If semantic information is missing, return {"semantic_obligations":["question"]} instead. You retain implementation, semantic review, test-adequacy judgment and ordinary tools for any needed probes. Failed checks return new evidence for reconsideration.
Exact files:
'''+json.dumps(spec['files'],ensure_ascii=False)
    (root/'prompt.txt').write_text(prompt)
    paths=[Path(__file__),Path(cap.__file__),Path(cap.kd.__file__),Path(observed_session.__file__),Path(raw_receipts.__file__),Path(caller_registration.__file__),cap.kd.REPO/'engine/output/app_server_native.py',Path('/Users/mert/.codex/AGENTS.md'),Path('/Users/mert/.codex/config.toml'),Path('/Users/mert/.codex/helix-context/bin/runtime-b09051d7f65fa98b.py'),skill,root/'prompt.txt',root/'coding-source.json',prior/'coding-default-run/status.json',prior/'coding-default-run/native-events.jsonl']
    manifest={'model':'gpt-5.6-luna','effort':'high','max_semantic_turns':2,'blind_retries':0,'prior':str(prior),'classification':'Adaptive known coding candidate, reused prior control; default base, source-only output and caller mechanics','sha256':{str(p.resolve()):cap.kd.sha(p) for p in paths},'input_roots':{n:cap.kd.sha(cwd/n) for n in spec['files']},'limits':['Not a fresh pair; previous control was ephemeral, new candidate durable','Filesystem binding checks are not a concurrent-writer lock','Finite oracle, no general capability certification']}
    cap.kd.save(root/'manifest.json',manifest)


def bound(root,m):
    cap.verify(m)
    for name,digest in m['input_roots'].items():assert cap.kd.sha(root/'on'/name)==digest,name


def realize(root,m,raw,index):
    bound(root,m);stage=root/f'stage-{index}';stage.mkdir()
    (stage/'allocation.py').write_bytes(raw)
    (stage/'test_allocation.py').write_bytes((root/'on/test_allocation.py').read_bytes())
    digest=cap.kd.sha(stage/'allocation.py');begin=time.perf_counter()
    checks=cap.grade(root,'coding',stage,'')
    assert cap.kd.sha(stage/'allocation.py')==digest
    bound(root,m);pending=root/'on/caller-pending.py';pending.write_bytes(raw)
    bound(root,m);os.replace(pending,root/'on/allocation.py')
    assert cap.kd.sha(root/'on/allocation.py')==digest
    return {'checks':checks,'source_sha256':digest,'caller_seconds':time.perf_counter()-begin,'engine_active':True}


def run(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());target=root/'results.json'
    if target.exists():raise ValueError('No retry')
    r={'state':'RUNNING','turns':[]};cap.kd.save(target,r)
    try:
        bound(root,m)
        with Session(m['model'],root/'on',root/'run',root/'on/.agents/skills/helixcontext/SKILL.md') as s:
            prompt=attach(s,(root/'prompt.txt').read_text())
            for index in range(1,m['max_semantic_turns']+1):
                answer,turn=s.turn(prompt);row={'answer':answer,'native':turn};r['turns'].append(row);r['usage']=dict(s.total);cap.kd.save(target,r)
                raw=source(answer);row['source_sha256']=__import__('hashlib').sha256(raw).hexdigest()
                # Only a finite behavioral check failure returns to the model.
                # Binding, parse and infrastructure failures remain explicit stops.
                try:row['completion']=realize(root,m,raw,index)
                except AssertionError as exc:
                    receipt=root/f'stage-{index}-caller-grade.json'
                    if not receipt.exists() or json.loads(receipt.read_text())['exit_code']==0:raise
                    row['check_failure']=json.loads(receipt.read_text());cap.kd.save(target,r)
                    if index==m['max_semantic_turns']:raise
                    prompt='Caller has not published. Reassess the exact failure evidence and return a replacement module or unresolved semantic questions.\n'+receipt.read_text()
                    continue
                r['state']='AWAITING_AUDIT';cap.kd.save(target,r);break
        if s.failed:raise RuntimeError('Native/raw capture failed')
        if r['state']!='AWAITING_AUDIT':raise RuntimeError('No verified publication')
        r['raw_capture']=s.capture_status;cap.kd.save(target,r)
        print(json.dumps({'state':r['state'],'usage':r['usage'],'turns':len(r['turns']),'raw_calls':s.capture_status['calls']}))
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));cap.kd.save(target,r);raise


if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
