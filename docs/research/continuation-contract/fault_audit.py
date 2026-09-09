"""Fault-inject the actual frozen V1 caller stage, with no native/model call.
The extracted AST statements are executed unchanged; this is not a replacement
Engine or a simulated benchmark token receipt.
"""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import time
import caller_patch_pair as v1
import audit

HERE=Path(__file__).resolve().parent


def stage():
    tree=ast.parse(Path(v1.__file__).read_text())
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    loop=next(n for n in run.body if isinstance(n,ast.For) and isinstance(n.iter,ast.Subscript))
    body=next(n for n in loop.body if isinstance(n,ast.Try)).body
    start=next(i for i,n in enumerate(body) if isinstance(n,ast.Assert) and "('CONTRACT.md', 'check_contract.py')" in ast.unparse(n))
    selected=body[start:]
    function=ast.parse('def exercise(cwd,spec,response,row,root,arm):\n pass\n').body[0]
    function.body=selected
    module=ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[]))
    scope=dict(vars(v1));exec(compile(module,'<frozen-v1-caller-stage>','exec'),scope)
    return scope,hashlib.sha256(ast.dump(ast.Module(body=selected,type_ignores=[]),include_attributes=False).encode()).hexdigest()


def run():
    results={};started=time.perf_counter();original_replace=v1.os.replace
    for fault in ('none','stale_before_apply','contract_changes_during_check','source_changes_before_replace','semantic_failure','checker_exception'):
        with tempfile.TemporaryDirectory(prefix='helix-caller-fault-') as directory:
            root=Path(directory);cwd=root/'on';cwd.mkdir()
            sources={'CONTRACT.md':(HERE/'CONTRACT.md').read_text(),'check_contract.py':v1.checker(),'queue_state.py':v1.BROKEN}
            for name,text in sources.items():(cwd/name).write_text(text)
            spec={'source_hashes':{name:v1.sha(text.encode()) for name,text in sources.items()}}
            response={'source':audit.GOOD if fault!='semantic_failure' else audit.GOOD.replace('type(value) is not int','not isinstance(value,int)'),'assessment':'Offline fixture assessment only','unresolved':[]}
            row={};scope,stage_hash=stage();state={'injection_executed':False};error=None
            if fault=='stale_before_apply':
                (cwd/'queue_state.py').write_text('# external edit\n'+v1.BROKEN);state['injection_executed']=True
            entry=(cwd/'queue_state.py').read_bytes()
            def check(folder,where,name):
                if fault=='checker_exception':state['injection_executed']=True;raise OSError('injected checker unavailable')
                value=v1.check(folder,where,name)
                if fault=='contract_changes_during_check':
                    (cwd/'CONTRACT.md').write_text(sources['CONTRACT.md']+'\nNEW AUTHORITY: batch length must not exceed two.\n')
                    state['injection_executed']=True
                return value
            scope['check']=check
            def replace(src,dst):
                if fault=='source_changes_before_replace':
                    Path(dst).write_text('# intervening writer edit\n'+v1.BROKEN);state['injection_executed']=True
                return original_replace(src,dst)
            try:
                v1.os.replace=replace
                scope['exercise'](cwd,spec,response,row,root,'on')
            except Exception as exc:error=type(exc).__name__+': '+str(exc)
            finally:v1.os.replace=original_replace
            current=(cwd/'queue_state.py').read_bytes()
            results[fault]={'error':error,'reported_pass':row.get('passed',False),
                'injection_executed':state['injection_executed'],'source_equals_entry':current==entry,
                'source_equals_proposed':current==response['source'].encode(),
                'protected_contract_still_bound':v1.sha((cwd/'CONTRACT.md').read_bytes())==spec['source_hashes']['CONTRACT.md'],
                'check_exit':(row.get('checks') or {}).get('exit_code')}
    assert results['none']['reported_pass']
    assert results['stale_before_apply']['error'] and results['stale_before_apply']['source_equals_entry']
    assert results['contract_changes_during_check']['reported_pass'] and not results['contract_changes_during_check']['protected_contract_still_bound']
    assert results['source_changes_before_replace']['reported_pass'] and results['source_changes_before_replace']['injection_executed']
    assert not results['semantic_failure']['reported_pass'] and results['semantic_failure']['check_exit']!=0 and not results['semantic_failure']['source_equals_entry']
    assert not results['checker_exception']['reported_pass'] and results['checker_exception']['source_equals_proposed']
    return {'classification':'OFFLINE_FAILURE_BOUNDARY_AUDIT_WITH_GAPS','native_calls':0,
        'driver_sha256':v1.sha(Path(v1.__file__).read_bytes()),'stage_ast_sha256':stage_hash,
        'fault_audit_sha256':v1.sha(Path(__file__).read_bytes()),'results':results,'seconds':time.perf_counter()-started,
        'disposition':'V1 remains bounded single-writer development evidence; not production-safe concurrent publication or automatic recovery',
        'limits':['Faults are deliberately injected, not observed in previous native trials',
                  'Actual frozen caller stage and real checker execute; no synthetic model token counters',
                  'No runtime or Engine implementation changed']}

if __name__=='__main__':
    result=run();(HERE/'FAULT_AUDIT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
