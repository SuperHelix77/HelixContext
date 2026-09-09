"""Declared resource-budget amendment; preserve original stopped V3 unchanged.

Continue the already-frozen candidate once. Never rerun/select a new control,
change prompts, remove reasoning, or silently relabel the original overrun.
"""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from completion_pair import sha,save,expected_ids,index_source
from integrated_runtime import Runtime
from native_usage import validate_resume,aggregate
from trace_profile import profile
import app_server_native


def run(root):
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());original=json.loads((root/'results.json').read_text())
    assert original['state']=='STOPPED' and len(original['rows'])==1
    control=original['rows'][0]
    assert control['arm']=='off' and control['passed'] and control['overrun']
    assert not (root/'receipts/on').exists()
    assert all(sha(Path(p).read_bytes())==h for p,h in m['dependencies'].items())
    cwd=root/'tasks/on';prompt=(root/'on-prompt.txt').read_text()
    assert sha(prompt.encode())==m['prompts']['on']
    assert all(sha((cwd/n).read_bytes())==h for n,h in m['preparation']['on']['source_hashes'].items())
    amendment={'schema':'helix.budget_amendment.v1','created_at':datetime.now(timezone.utc).isoformat(),
        'original_manifest_sha256':sha((root/'manifest.json').read_bytes()),'original_stopped_result_sha256':sha((root/'results.json').read_bytes()),
        'original_control_overrun_preserved':True,'new_native_calls':1,'candidate_prompt_sha256':m['prompts']['on'],
        'candidate_code_and_prompt_unchanged':True,'candidate_post_call_limits':{'input_tokens':80000,'output_tokens':6000},
        'combined_reported_limits':{'input_tokens':250000,'output_tokens':9000},
        'reason':'App-server control exceeded 150000 input. Measure frozen candidate without repeating expensive control.',
        'classification':'Budget-amended continuation, not untouched preregistration. No causal component or general parity claim.',
        'scope':'Native budget only. Server/parent costs and lost transient pre-stop preparation counters unmeasured.',
        'driver_sha256':sha(Path(__file__).read_bytes())}
    save(root/'budget-amendment.json',amendment)
    r=Runtime(root/'stores/on','release-fixture','Helix-Output','s3')
    reference=m['preparation']['on']['costs']['catalog']['reference']
    rows=[control]
    try:
        out=root/'receipts/on';answer,status=app_server_native.native(m['model'],cwd,prompt,out)
        u=validate_resume(status,m['model'],prompt,(out/'prompt.txt').read_text());anatomy=profile(out/'events.jsonl')
        assert u==anatomy['native_usage'] and status['events_sha256']==anatomy['events_sha256']
        unchanged=all(sha((cwd/n).read_bytes())==h for n,h in m['preparation']['on']['source_hashes'].items())
        if not unchanged:raise ValueError('Source changed')
        completion=r.complete(reference,answer,cwd/'result.jsonl')
        actual=(cwd/'result.jsonl').read_bytes()
        passed=sha(actual)==m['expected_sha256'] and json.loads(answer)==expected_ids()
        row={'arm':'on','usage':u,'elapsed_seconds':status['elapsed_seconds'],'artifact_exact':sha(actual)==m['expected_sha256'],
             'artifact_sha256':sha(actual),'source_unchanged':unchanged,'passed':passed,'completion':completion,
             'anatomy':anatomy,'events_sha256':status['events_sha256'],'native_events_sha256':status['native_events_sha256'],
             'engine_accounting':r.accounting(),'overrun':any(u[k]>v for k,v in amendment['candidate_post_call_limits'].items())}
        rows.append(row);combined=aggregate([v['usage'] for v in rows])
        savings={k:100*(1-u[k]/control['usage'][k]) for k in ('input_tokens','output_tokens')}
        within=not row['overrun'] and not any(combined[k]>v for k,v in amendment['combined_reported_limits'].items())
        state='STOPPED' if not passed or not within else 'SOL_V1_80_80_CANDIDATE' if min(savings.values())>=80 else 'SOL_V1_75_CANDIDATE' if min(savings.values())>=75 else 'RESIDUAL_DIAGNOSIS_ONLY'
        result={'state':state,'classification':amendment['classification'],'budget_amended':True,'rows':rows,
                'savings_percent':savings,'combined_native_usage':combined,'within_amended_budget':within,
                'capability_parity':'unestablished; bounded exact checks only','original_stop_retained':'results.json'}
        save(root/'followup-results.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    except Exception as exc:
        save(root/'followup-results.json',{'state':'STOPPED','rows':rows,'budget_amended':True,'error':str(exc),'note':'Launched failed candidate usage stays in receipts and must be charged.'});raise


if __name__=='__main__':run(sys.argv[1])
