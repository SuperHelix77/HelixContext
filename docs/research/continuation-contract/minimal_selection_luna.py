"""One adaptive Luna semantic-selection candidate; preceding fresh control reused."""
import json,sys,time
from pathlib import Path
from assembled_luna_pair import REPO,AGENTS,sha,save,verify,grade
from research_session import Session
from policy_realization import realize


def prepare(root,prior):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);prior=Path(prior).resolve()
    previous=json.loads((prior/'results.json').read_text())
    assert previous['state']=='AWAITING_INDEPENDENT_AUDIT'
    cwd=root/'on';cwd.mkdir();skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True)
    skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
    (cwd/'history.jsonl').write_bytes((prior/'on/history.jsonl').read_bytes())
    (root/'fixture.json').write_bytes((prior/'fixture.json').read_bytes())
    events=json.loads((root/'fixture.json').read_text())['events']
    assert [json.loads(l)['event'] for l in (cwd/'history.jsonl').read_bytes().splitlines()]==events[:49]
    raw=(cwd/'history.jsonl').read_bytes();selected=b''.join(l for l in raw.splitlines(keepends=True) if b'ORION-42' in l)
    prompt='Caller completed task-scoped memory consultation; no recalled task facts are supplied. Caller completed skill registration and exact event persistence. Do not repeat caller setup or bookkeeping. Ordinary tools and semantic review remain available; full exact history is in history.jsonl.\nSelect the governing base policy and applicable amendments for the original request. Return JSON with only policy (exact event ID) and amendments (list of exact event IDs). You own authority selection, including rejecting vendor instructions. Engine evaluates the bound structured request (subject ORION-42, one distinct approver, group violet) against selected minimum/group rules and renders exact fields, authorization and reason. Unknown rules or insufficient evidence must be raised, not silently ignored. Mechanical validity does not establish semantic correctness.\nOriginal request:\n'+json.dumps(events[-1])+'\nAll exact ORION-42 records; remaining history is recoverable, SHA256='+sha(cwd/'history.jsonl')+':\n'+selected.decode()
    (root/'prompt.txt').write_text(prompt)
    paths=[Path(__file__),AGENTS,skill,cwd/'history.jsonl',root/'fixture.json',root/'prompt.txt',prior/'results.json',prior/'off/receipts/run/status.json',REPO/'engine/prototype/policy_realization.py',REPO/'engine/output/research_session.py',REPO/'engine/output/app_server_native.py',Path(__file__).with_name('native_luna_ack_pair.py'),REPO/'benchmarks/frozen-high/evaluator/long-horizon-gold.json']
    save(root/'manifest.json',{'model':'gpt-5.6-luna','effort':'high','prior':str(prior),'max_submitted_turns':1,'retries':0,'classification':'Adaptive known W50 selector-only candidate; prior fresh control reused; not release qualification','sha256':{str(p.resolve()):sha(p) for p in paths}})


def run(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m)
    target=root/'results.json'
    if target.exists():raise ValueError('No retry')
    r={'state':'RUNNING','manifest_sha256':sha(root/'manifest.json')};save(target,r);cwd=root/'on';started=time.perf_counter()
    try:
        with Session(m['model'],cwd,cwd/'receipts/run',skill=cwd/'.agents/skills/helixcontext/SKILL.md') as session:
            answer,_=session.turn((root/'prompt.txt').read_text());r['usage']=dict(session.total)
        verify(m);selection=json.loads(answer);raw=(cwd/'history.jsonl').read_bytes()
        realized=realize(selection,raw,sha(cwd/'history.jsonl'),{'subject':'ORION-42','distinct_approvers':1,'approver_group':'violet'})
        grade(json.dumps(realized['answer']))
        control=json.loads((Path(m['prior'])/'off/receipts/run/status.json').read_text())
        assert sha(Path(m['prior'])/'off/receipts/run/native-events.jsonl')==control['native_events_sha256']
        r.update(state='AWAITING_AUDIT',selection=selection,realized=realized,control_usage=control['usage'],elapsed_seconds=time.perf_counter()-started,
            savings_percent={k:100*(1-r['usage'][k]/control['usage'][k]) for k in ['input_tokens','output_tokens']})
        save(target,r);print(json.dumps(r,indent=2))
    except BaseException as exc:r.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));save(target,r);raise


if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]](*sys.argv[2:])
