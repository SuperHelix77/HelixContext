"""Finish the five unrun arms after exact caller-registration recovery.

The first candidate is preserved, never rerun. Original failed wrapper receipts
remain intact; completion/results have an explicit post-hoc configuration audit.
"""
import json
from pathlib import Path
import sys
import luna_varied_coding_v1 as v1
import config_bound_session as config


def freeze(root):
    root=Path(root).resolve();path=root/'continuation-manifest.json';m=json.loads(path.read_text())
    for p in [Path(__file__),Path(__file__).with_name('luna_varied_coding_continue_audit.py')]:m['sha256'][str(p.resolve())]=v1.sha(p)
    v1.save(path,m);print(v1.sha(path))


def run(root):
    root=Path(root).resolve();m=json.loads((root/'continuation-manifest.json').read_text());path=root/'continuation-results.json'
    if path.exists():raise ValueError('Continuation already attempted; no implicit retry')
    recovered=json.loads(Path(m['recovered_first_row']).read_text());prior=json.loads((root/'results.json').read_text())
    assert recovered['model_calls_added']==0 and recovered['completion']['published']
    assert prior['state']=='STOPPED_PENDING_AUDIT' and len(prior['rows'])==1
    first=prior['rows'][0];first['completion']=recovered['completion'];first['finite_checks']='PASS';first['recovered_guard']=True
    first['turns'][0]['completion']=recovered['completion']
    result={'state':'RUNNING','rows':[first],'manifest_sha256':v1.sha(root/'continuation-manifest.json'),
            'classification':'Same planned three pairs with explicit configuration-audit amendment; first candidate preserved, five new arms; not untouched preregistration'}
    v1.save(path,result)
    original_verify=v1.verify;original_rpc=v1.observed_session.RPC
    def bound(manifest):
        original_verify(manifest)
        config.validate(Path(manifest['config_snapshot']).read_bytes(),Path(manifest['shared_config']).read_bytes())
    class KernelRPC(original_rpc):
        def call(self,method,params):
            if method=='thread/start':params={**params,'config':{**params['config'],'model_instructions_file':str(v1.BASE)}}
            return super().call(method,params)
    v1.verify=bound
    try:
        for case,arm in m['remaining_order']:
            v1.verify_initial(root,m,case,arm);cwd=root/case/arm
            assert not (cwd/'.codex').exists() and not (cwd/'.codex').is_symlink()
            v1.observed_session.RPC=KernelRPC if arm=='on' else original_rpc
            row={'case':case,'arm':arm,'turns':[]};result['rows'].append(row);v1.save(path,result)
            with config.Session(m['model'],cwd,root/case/(arm+'-run'),cwd/'.agents/skills/helixcontext/SKILL.md' if arm=='on' else None) as session:
                prompt=v1.caller_registration.attach(session,(root/case/(arm+'-prompt.txt')).read_text())
                for index in range(1,(m['max_semantic_turns'] if arm=='on' else 1)+1):
                    answer,turn=session.turn(prompt);current={'answer':answer,'native':turn};row['turns'].append(current);row['usage']=dict(session.total);v1.save(path,result)
                    if arm=='off':
                        bound(m);row['completion']=v1.grade(case,cwd,root/case/'off-check.json');break
                    try:raw=v1.source(answer)
                    except (ValueError,SyntaxError) as exc:
                        row['completion']={'exit_code':None,'semantic_attention_required':str(exc)};break
                    completion=v1.realize(root,m,case,raw,index);current['completion']=completion;row['completion']=completion;v1.save(path,result)
                    if completion['exit_code']==0:break
                    prompt='Caller has not published. Reassess these exact check failures and return a replacement module or unresolved semantic questions.\n'+json.dumps(completion)
            if session.failed:raise RuntimeError('Native/configuration/raw capture failed')
            row['raw_capture']=session.capture_status;row['finite_checks']='PASS' if row['completion']['exit_code']==0 else 'FAIL'
            bound(m);v1.save(path,result)
            print(json.dumps({'case':case,'arm':arm,'usage':row['usage'],'finite_checks':row['finite_checks']}),flush=True)
        result['state']='AWAITING_CONTINUATION_AUDIT';v1.save(path,result)
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));v1.save(path,result);raise
    finally:v1.verify=original_verify;v1.observed_session.RPC=original_rpc


if __name__=='__main__':{'freeze':freeze,'run':run}[sys.argv[1]](sys.argv[2])
