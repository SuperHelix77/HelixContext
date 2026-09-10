"""Verify exact offline artifacts and keep calibration separate from admission."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def sha(raw):return hashlib.sha256(raw).hexdigest()


def verify(private_root=None):
    closure=json.loads((HERE/'CLOSURE.json').read_text())
    for name,digest in closure['files'].items():assert sha((HERE/name).read_bytes())==digest,name
    cal=json.loads((HERE/'CALIBRATION.json').read_text())
    rows={r['case']:r for r in cal['rows']}
    index=json.loads((HERE/'artifacts/INDEX.json').read_text())
    assert len(index)==len(rows)==18
    for entry in index:
        values={};r=rows[entry['case']]
        for kind,ref in entry['evidence'].items():
            raw=(HERE/'artifacts/objects'/ref['sha256']).read_bytes()
            assert len(raw)==ref['bytes'] and sha(raw)==ref['sha256']
            values[kind]=raw
        request=json.loads(values['request.json']);receipt=json.loads(values['receipt.json'])
        outcome=json.loads(values['stdout'])
        assert request['query']==r['query'] and receipt['state']=='OBSERVATIONS_RECORDED'
        assert receipt['request_sha256']==sha(values['request.json'])
        assert receipt['program_sha256']==sha(values['program.py'])==r['program_sha256']
        assert receipt['binding_sha256']==sha(values['binding.json'])
        assert receipt['stdout_sha256']==sha(values['stdout'])==r['stdout_sha256']
        assert receipt['stderr_sha256']==sha(values['stderr'])
        assert outcome['contract_failures']==r['contract_failures']==r['expected_failures']
        assert outcome['control_passes']==9 and len(outcome['targeted_results'])==9
    decision=json.loads((HERE/'RESULT.json').read_text())
    scope=json.loads((HERE/'SCOPE_AUDIT.json').read_text())
    assert decision['state']=='OFFLINE_PROTOTYPE_REJECTED' and not decision['model_profile_activated']
    assert scope['query_only_interface_verdict']=='REJECT_AS_SPECIFIED'
    assert decision['native_benchmark_calls']==decision['calls_authorized_by_this_report']==0
    result={'state':'EVIDENCE_VERIFIED_PROTOTYPE_REMAINS_REJECTED','public_bindings':len(closure['files']),
            'mechanical_cases':18,'comparison_rows':162,'native_calls':0}
    if private_root:
        root=Path(private_root);m=json.loads((root/'manifest.json').read_text())
        assert sha((root/'manifest.json').read_bytes())==cal['manifest_sha256']
        for name,digest in m['files'].items():assert sha(Path(name).read_bytes())==digest,name
        for row in cal['rows']:
            b=json.loads((root/row['case']/'binding.json').read_text())
            for name,digest in b['files'].items():assert sha(Path(name).read_bytes())==digest,name
        result['original_bound_source_files']='PASS'
    print(json.dumps(result,indent=2))


if __name__=='__main__':verify(sys.argv[1] if len(sys.argv)>1 else None)
