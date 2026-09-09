"""Explicit post-outcome completion of two caller obligations; no native retry.

Exact wording match is a one-receipt adjudication, not a general obligation parser.
Preserves the failed runner result and never edits the model-authored source.
"""
import json
import os
import sys
import time
from pathlib import Path
import luna_caller_coding as driver
from app_server_native import usage


def recover(root, out):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());driver.bound(root,m)
    failed=json.loads((root/'results.json').read_text())
    assert failed['state']=='STOPPED_PENDING_AUDIT' and failed['error']=='Unresolved semantics: no publication'
    assert len(failed['turns'])==1
    if (root/'recovery.json').exists():raise ValueError('Recovery already adjudicated')
    p=root/'run';s=json.loads((p/'status.json').read_text())
    assert s['state']=='closed' and driver.cap.kd.sha(p/'native-events.jsonl')==s['native_events_sha256']
    events=[json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
    steps=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
    assert usage(steps[-1])==s['usage']==failed['usage']
    for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
        assert sum(e['params']['tokenUsage']['last'][native] for e in steps)==s['usage'][key]
    answer=(p/'turn-1-answer.txt').read_text();assert answer==failed['turns'][0]['answer']
    obj=driver.cap.parse(answer)
    assert obj['unresolved']==['Caller must run the independent allocation oracle against the exact source.',
                              'Caller must atomically publish allocation.py only after all checks succeed.']
    recovery={'classification':'Post-outcome caller-obligation completion; original runner FAIL retained',
        'original_result_sha256':driver.cap.kd.sha(root/'results.json'),
        'recovery_script_sha256':driver.cap.kd.sha(Path(__file__)),
        'original_unresolved':obj['unresolved'],'usage':s['usage'],
        'native_sha256':s['native_events_sha256'],'segments':len(steps),
        'native_calls_added_by_recovery':0,'general_workflow_parity':'NOT_ESTABLISHED'}
    start=time.perf_counter();stage=root/'recovery-stage';stage.mkdir(exist_ok=False)
    raw=obj['source'].encode();(stage/'allocation.py').write_bytes(raw)
    (stage/'test_allocation.py').write_bytes((root/'on/test_allocation.py').read_bytes())
    recovery['checks']=driver.cap.grade(root,'coding',stage,answer)
    assert (stage/'allocation.py').read_bytes()==raw
    driver.bound(root,m)
    pending=root/'on/caller-recovered.py';pending.write_bytes(raw)
    driver.bound(root,m);os.replace(pending,root/'on/allocation.py')
    assert (root/'on/allocation.py').read_bytes()==raw
    recovery.update(state='CALLER_OBLIGATIONS_COMPLETED',source_sha256=driver.cap.kd.sha(stage/'allocation.py'),
                    recovery_seconds=time.perf_counter()-start,
                    obligation_status=['Exact returned source passed public suite and 4433-case allocation oracle',
                                       'Exact returned source atomically published after bound-input checks'])
    prior=Path(m['prior']);control=json.loads((prior/'coding-default-run/status.json').read_text())
    assert driver.cap.kd.sha(prior/'coding-default-run/native-events.jsonl')==control['native_events_sha256']
    a,b=control['usage'],s['usage'];recovery['control_usage']=a
    recovery['savings_percent']={k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')}
    recovery['uncached_savings_percent']=100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens']))
    driver.cap.kd.save(root/'recovery.json',recovery);driver.cap.kd.save(Path(out),recovery)
    driver.cap.kd.save(root/'hud-status.json',{**s,'state':'completed','runner':'app-server','source_status_sha256':driver.cap.kd.sha(p/'status.json')})
    print(json.dumps(recovery,indent=2))


if __name__=='__main__':recover(*sys.argv[1:])
