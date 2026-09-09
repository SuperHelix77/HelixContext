"""Caller-owned realization of Luna-authored code; exact staging and recovery.

One adaptive candidate, reused native control. All failed turns remain charged.
No production configuration is changed; kernel/tool/High settings stay explicit.
"""
import json
import os
import sys
import time
from pathlib import Path
import luna_capability_pair as cap
from caller_registration import attach
import caller_registration


def prepare(root, prior):
    root,prior=Path(root).resolve(),Path(prior).resolve();root.mkdir(parents=True,exist_ok=False)
    spec=json.loads((prior/'coding-source.json').read_text());cap.kd.save(root/'coding-source.json',spec)
    cwd=root/'on';cwd.mkdir()
    for name,text in spec['files'].items():(cwd/name).write_text(text)
    kernel=root/'luna-base-v1.md';kernel.write_bytes((prior/'luna-base-v1.md').read_bytes())
    skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True)
    skill.write_bytes((prior/'coding/helix/.agents/skills/helixcontext/SKILL.md').read_bytes())
    prompt=cap.COMMON+spec['task']+'''
Caller-execution agreement: you own the implementation, semantic assessment and test-adequacy judgment. Caller will stage your exact source, execute the existing unittest suite and an independent allocation oracle, and atomically publish allocation.py only after success against unchanged protected files. No integration code or model-side bookkeeping is needed. Do not claim checks already ran. Leave the original allocation.py unchanged for bound publication. Ordinary tools and novel semantic probes remain available when needed.
Return JSON with source (complete Python module string), assessment (your substantive correctness justification and limits), and unresolved (array of unresolved obligations). Unknown or failed checks return for semantic reconsideration; no repair is silently made by the caller. Review the implementation before delegating it; finite PASS is not semantic completeness.
Exact current source and existing tests:
'''+json.dumps(spec['files'],ensure_ascii=False)
    (root/'prompt.txt').write_text(prompt)
    paths=[Path(__file__),Path(cap.__file__),Path(caller_registration.__file__),Path(cap.kd.__file__),kernel,skill,
           root/'prompt.txt',root/'coding-source.json',Path('/Users/mert/.codex/AGENTS.md'),
           cap.kd.REPO/'engine/output/research_session.py',cap.kd.REPO/'engine/output/app_server_native.py',
           prior/'manifest.json',prior/'coding-default-run/status.json',prior/'coding-default-run/native-events.jsonl']
    cap.kd.save(root/'manifest.json',{'model':'gpt-5.6-luna','effort':'high','prior':str(prior),
        'kernel':str(kernel),'max_semantic_turns':2,'blind_retries':0,
        'classification':'Adaptive known coding fixture; reused control; caller realization, supplied source and registration attestation combined',
        'input_roots':{n:cap.kd.sha(cwd/n) for n in spec['files']},
        'sha256':{str(p):cap.kd.sha(p) for p in paths},
        'closure':'Model reviews before delegation; re-enter only on failed checks. Explicit unresolved obligations prevent publication.',
        'limits':['No holdout or general parity; reuse-order/cache confounds.',
                  'Filesystem identity checks are not an adversarial concurrent-writer lock.',
                  'Caller staging is not a security sandbox for arbitrary untrusted code.']})
    print(cap.kd.sha(root/'manifest.json'))


def bound(root,m):
    cap.verify(m)
    for name,h in m['input_roots'].items():assert cap.kd.sha(root/'on'/name)==h,name


def run(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());state=root/'results.json'
    if state.exists():raise ValueError('No retry')
    r={'state':'RUNNING','turns':[],'manifest_sha256':cap.kd.sha(root/'manifest.json')};cap.kd.save(state,r)
    cwd=root/'on';start=time.perf_counter()
    cap.kd.research_session.RPC=cap.kd.rpc_with_base(Path(m['kernel']))
    try:
        bound(root,m)
        with cap.kd.research_session.Session(m['model'],cwd,root/'run',cwd/'.agents/skills/helixcontext/SKILL.md') as s:
            prompt=attach(s,(root/'prompt.txt').read_text())
            for index in range(m['max_semantic_turns']):
                answer,turn=s.turn(prompt);row={'native':turn,'answer':answer};r['turns'].append(row)
                r['usage']=s.total;cap.kd.save(state,r);bound(root,m)
                obj=cap.parse(answer)
                assert isinstance(obj.get('source'),str) and obj['source']
                assert isinstance(obj.get('assessment'),(str,dict)) and obj['assessment']
                assert isinstance(obj.get('unresolved'),list) and not obj['unresolved'],'Unresolved semantics: no publication'
                stage=root/f'stage-{index+1}';stage.mkdir()
                (stage/'allocation.py').write_bytes(obj['source'].encode())
                (stage/'test_allocation.py').write_bytes((cwd/'test_allocation.py').read_bytes())
                original=cap.kd.sha(stage/'allocation.py');begin=time.perf_counter()
                try:
                    row['checks']=cap.grade(root,'coding',stage,answer)
                    assert cap.kd.sha(stage/'allocation.py')==original
                    bound(root,m)
                except Exception as exc:
                    row['check_failure']=str(exc);row['caller_check_seconds']=time.perf_counter()-begin
                    cap.kd.save(state,r)
                    if index+1==m['max_semantic_turns']:raise
                    receipt=root/(stage.name+'-caller-grade.json')
                    prompt='The caller did not publish. Checks produced new evidence; reassess and return the same complete source/assessment/unresolved schema. Exact check receipt:\n'+(receipt.read_text() if receipt.exists() else str(exc))
                    continue
                row['caller_check_seconds']=time.perf_counter()-begin
                pending=cwd/'caller-pending.py';pending.write_bytes(obj['source'].encode())
                bound(root,m);os.replace(pending,cwd/'allocation.py')
                assert cap.kd.sha(cwd/'allocation.py')==original
                row['published_sha256']=original;row['assessment']=obj['assessment']
                r.update(state='AWAITING_AUDIT',elapsed_seconds=time.perf_counter()-start)
                cap.kd.save(state,r);break
        if r['state']!='AWAITING_AUDIT':raise RuntimeError('No verified publication')
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT',error=str(exc));cap.kd.save(state,r);raise
    finally:cap.kd.research_session.RPC=cap.kd.OriginalRPC


if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
