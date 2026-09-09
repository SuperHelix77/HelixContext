"""Explicit evaluator correction: additive tests are allowed by the frozen prompt."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import app_server_native
import astra_patch_pair as base
from completion_pair import sha,save


def preserved_tests(original,current):
    def contained(old,new):
        for node in old:
            if isinstance(node,ast.ClassDef):
                matches=[n for n in new if isinstance(n,ast.ClassDef) and n.name==node.name]
                if len(matches)!=1:return False
                match=matches[0]
                if [ast.dump(n) for n in node.bases+node.decorator_list]!=[ast.dump(n) for n in match.bases+match.decorator_list]:return False
                if not contained(node.body,match.body):return False
            elif sum(ast.dump(n)==ast.dump(node) for n in new)!=1:return False
        return True
    try:return contained(ast.parse(original).body,ast.parse(current).body)
    except SyntaxError:return False


def grade(root,arm,m):
    cwd=root/'tasks'/arm
    preserved=all(sha((cwd/k).read_bytes())==v for k,v in m['sources'].items() if k not in ('queue_state.py','test_contract.py'))
    preserved=preserved and preserved_tests(base.TESTS,(cwd/'test_contract.py').read_text())
    logs=[];codes=[]
    # Execute the untouched original suite in a separate temporary directory.
    with tempfile.TemporaryDirectory() as temp:
        td=Path(temp);(td/'test_contract.py').write_text(base.TESTS);(td/'queue_state.py').write_bytes((cwd/'queue_state.py').read_bytes())
        commands=[([sys.executable,'-m','unittest','-v','test_contract'],td),
                  ([sys.executable,str(root/'checker.py'),str(cwd/'queue_state.py')],cwd),
                  ([sys.executable,'-m','unittest','-v','test_contract'],cwd)]
        for argv,location in commands:
            p=subprocess.run(argv,cwd=location,capture_output=True);codes.append(p.returncode);logs.append(p.stdout+p.stderr)
    raw=b'\n'.join(logs);(root/f'{arm}-corrected-checker.log').write_bytes(raw)
    return {'checks_passed':preserved and all(c==0 for c in codes),'preserved_original_tests':preserved,'check_exit_codes':codes,'checker_log_sha256':sha(raw)}


def run(root):
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());original=(root/'results.json').read_bytes()
    assert json.loads(original)['state']=='STOPPED_GATE_OR_BUDGET'
    assert sha(Path(base.__file__).read_bytes())==m['driver_sha256']
    assert sha((root/'checker.py').read_bytes())==m['checker_sha256']
    for a in ('off','on'):assert sha((root/f'{a}-prompt.txt').read_bytes())==m['prompts'][a]
    assert not (root/'receipts/on').exists()
    for f,h in m['sources'].items():assert sha((root/'tasks/on'/f).read_bytes())==h
    off=json.loads((root/'receipts/off/status.json').read_text())
    corrected=grade(root,'off',m);assert corrected['checks_passed']
    assert all(off['usage'][k]<=v for k,v in m['thresholds'].items())
    amendment={'reason':'Original prompt allows adding tests; whole-file hash gate incorrectly rejected those additions. Original test AST retained and original suite run independently.',
        'original_stopped_sha256':sha(original),'driver_sha256':sha(Path(__file__).read_bytes()),'control_corrected':corrected,
        'candidate_prompt_unchanged':True,'remaining_native_calls':1,'thresholds_unchanged':m['thresholds'],
        'classification':'Evaluator-corrected development pair; not untouched preregistration'}
    assert not (root/'evaluator-correction.json').exists();save(root/'evaluator-correction.json',amendment)
    _,on=app_server_native.native(base.MODEL,root/'tasks/on',(root/'on-prompt.txt').read_text(),root/'receipts/on')
    on_grade=grade(root,'on',m)
    rows=[{'arm':a,'usage':s['usage'],'elapsed_seconds':s['elapsed_seconds'],'events_sha256':s['events_sha256'],
           'native_events_sha256':s['native_events_sha256'],'behavioral_checks':g} for a,s,g in [('off',off,corrected),('on',on,on_grade)]]
    savings={k:100*(1-on['usage'][k]/off['usage'][k]) for k in ('input_tokens','output_tokens')}
    pass_gate=on_grade['checks_passed'] and all(on['usage'][k]<=v for k,v in m['thresholds'].items())
    result={'state':('BOUNDED_TARGET_PASS' if min(savings.values())>=80 else 'BELOW_TARGET') if pass_gate else 'FAILED_CHECK_OR_BUDGET',
        'classification':amendment['classification'],'rows':rows,'savings_percent':savings,'original_stopped_sha256':sha(original),
        'correction_sha256':sha((root/'evaluator-correction.json').read_bytes()),'limitations':'Finite coding checks only; no general parity or total billing claim.'}
    assert (root/'results.json').read_bytes()==original
    save(root/'corrected-results.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':run(sys.argv[1])
