"""Hostile semantic-scope audit after mechanical calibration; zero model calls."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('query_scope_adapter',HERE/'adapter.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def audit():
    before=a.oblig.BASE/'baseline/workflow_memory.py'
    Old=a.oblig.load(before,'scope_reference')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='helix-query-scope-') as tmp:
        memory=Old(a.oblig.Store(Path(tmp)))
        memory.record('p','s','unrelated',b'other evidence')
        for query in ('unlisted_token','other evidence','OTHÉR','unlisted other'):
            words=a.oblig.re.findall(r'\w+',query,flags=a.oblig.re.UNICODE)
            full=memory.search('p',query,1)
            per_word=[memory.search('p',word,1) for word in words]
            rows.append({'query':query,'reference_all_matches_auxiliary':bool(full),
                'reference_single_word_union_matches_auxiliary':any(per_word)})
    assert rows[0]['reference_all_matches_auxiliary'] is False
    assert rows[1]['reference_all_matches_auxiliary'] is True
    assert rows[2]['reference_all_matches_auxiliary'] is True
    assert rows[3]['reference_all_matches_auxiliary'] is False
    assert rows[3]['reference_single_word_union_matches_auxiliary'] is True
    # Read-only proof of a distinct blind spot; no rerun is needed to rediscover it.
    calls=[n for n in ast.walk(ast.parse(a.TEMPLATE.read_bytes())) if isinstance(n,ast.Call)
           and isinstance(n.func,ast.Attribute) and n.func.attr=='search']
    assert len(calls)==1 and len(calls[0].args)==3
    assert isinstance(calls[0].args[2],ast.Constant) and calls[0].args[2].value==1
    valid=HERE.with_name('differential-obligations-v1')/'artifacts/valid-source.py'
    bad=valid.with_name('known_default_limit-source.py')
    assert valid.read_bytes().replace(b'def search(self,project,query,limit=10,',
        b'def search(self,project,query,limit=9,') == bad.read_bytes()
    result={'state':'SCOPE_FALSIFIER_CONFIRMED','native_calls':0,'reference_observations':rows,
        'query_only_interface_verdict':'REJECT_AS_SPECIFIED',
        'finding':'Scenario identifiers and tool description imply nonmatching auxiliary evidence, but parameterized queries can match it. Mechanical equivalence did not preserve that coverage precondition.',
        'default_limit_blind_spot':{'method_calls':1,'explicit_limit':1,
            'valid_sha256':a.sha(valid),'known_defect_sha256':a.sha(bad),
            'proof_scope':'These two sources differ only in the search default. Every search in this witness passes limit=1, so this witness cannot distinguish that change.'},
        'repair_required_before_any_use':'Either check and expose the query-dependent coverage preconditions, or narrow/rename all unsupported scope claims. Add the actual declared preconditions to future observation receipts; retain other tools for untested obligations.',
        'economic_gate':'Still HOLD_NATIVE: no whole-task 80/80 case even if scope were repaired'}
    a.save(HERE/'SCOPE_AUDIT.json',result)
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=='__main__':audit()
