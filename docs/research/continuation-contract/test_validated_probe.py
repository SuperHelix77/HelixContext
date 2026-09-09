import json
import pytest
from prepared_review import prepare
from validated_probe import execute

def setup(tmp_path):
    source=tmp_path/'source';source.mkdir()
    for name in ('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py'):(source/name).write_text('# fixture\n')
    evidence=tmp_path/'evidence';h=prepare(source,evidence)
    return source,evidence,h

def test_single_call_success_and_no_retry(tmp_path):
    source,evidence,h=setup(tmp_path);out=tmp_path/'run'
    r=execute(evidence,h,"from pathlib import Path\nassert Path('proposal.py').read_text()=='# fixture\\n'\nprint('novel check passed')\n",out)
    assert r['status']=='PROBE_PASS' and r['semantic_acceptance'] is None
    assert (out/'stdout.bin').read_text()=='novel check passed\n'
    with pytest.raises(FileExistsError):execute(evidence,h,'raise Exception()',out)

@pytest.mark.parametrize('fault',['stale_source','tampered_output','wrong_receipt'])
def test_bad_evidence_never_executes_probe(tmp_path,fault):
    source,evidence,h=setup(tmp_path)
    if fault=='stale_source':(source/'CONTRACT.md').write_text('changed')
    if fault=='tampered_output':(evidence/'check/stdout.bin').write_text('changed')
    if fault=='wrong_receipt':h='0'*64
    out=tmp_path/'run';r=execute(evidence,h,"raise AssertionError('must not execute')",out)
    assert not r['probe_started'] and r['status']=='EVIDENCE_INVALID_BEFORE_PROBE'

def test_novel_semantic_failure_retained(tmp_path):
    source,evidence,h=setup(tmp_path);out=tmp_path/'run';r=execute(evidence,h,"print('before failure',flush=True)\nassert False, 'new semantic violation'",out)
    assert r['status']=='PROBE_FAIL' and r['exit_code']!=0
    assert b'new semantic violation' in (out/'stderr.bin').read_bytes()
    assert b'before failure' in (out/'stdout.bin').read_bytes()

def test_probe_mutation_does_not_modify_original(tmp_path):
    source,evidence,h=setup(tmp_path);r=execute(evidence,h,"from pathlib import Path\nPath('proposal.py').write_text('changed')",tmp_path/'run')
    assert r['status']=='EVIDENCE_INVALID_AFTER_PROBE'
    assert (source/'proposal.py').read_text()=='# fixture\n'

def test_timeout_not_pass(tmp_path):
    source,evidence,h=setup(tmp_path);r=execute(evidence,h,'while True: pass',tmp_path/'run',timeout=.1)
    assert r['status']=='PROBE_TIMEOUT' and r['exit_code'] is None
