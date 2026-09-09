"""Bound candidate audit plus two explicitly retained reference comparisons."""
import hashlib
import json
import sys
from pathlib import Path
import luna_coding_decision_v2_audit as original
from app_server_native import usage


def audit(root):
    root=Path(root)
    original.audit(root,'LUNA_CODING_COMPOSED_V1_RAW_AUDIT.json')
    m=json.loads((root/'manifest.json').read_text())
    report=json.loads(Path(__file__).with_name('LUNA_CODING_COMPOSED_V1_RAW_AUDIT.json').read_text())
    requests=[json.loads(l) for l in (root/'run/requests.jsonl').read_text().splitlines()]
    starts=[r for r in requests if r.get('method')=='thread/start']
    assert len(starts)==1
    cfg=starts[0]['params']['config']
    assert cfg['model_instructions_file']==m['base_file'] and cfg['model_reasoning_effort']=='high'
    raw=[json.loads(l) for l in (root/'run/raw/raw-rollout.jsonl').read_text().splitlines()]
    meta=next(r['payload'] for r in raw if r.get('type')=='session_meta')
    base=Path(m['base_file']).read_bytes()
    assert meta['base_instructions']['text'].encode()==base
    reference=Path(m['fresh_reference']);rows=[];comparisons=[]
    candidate=report['candidate_usage']
    for name,rel in [('retained_native','off-run'),('retained_helix_default_base','run')]:
        path=reference/rel;status=json.loads((path/'status.json').read_text())
        wire=(path/'native-events.jsonl').read_bytes()
        assert hashlib.sha256(wire).hexdigest()==status['native_events_sha256']
        updates=[json.loads(l) for l in wire.splitlines() if b'thread/tokenUsage/updated' in l]
        assert status['state']=='closed' and status['model']==m['model'] and status['effort']=='high'
        assert usage(updates[-1])==status['usage']
        a=status['usage'];savings={k:100*(1-candidate[k]/a[k]) for k in ('input_tokens','output_tokens')}
        uncached=100*(1-(candidate['input_tokens']-candidate['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens']))
        rows.append({'arm':name,'usage':a,'native_sha256':status['native_events_sha256']})
        comparisons.append({'reference':name,'savings_percent':savings,'uncached_savings_percent':uncached})
    rows.append({'arm':'candidate','usage':candidate,'native_sha256':report['native_sha256'],'checks':'PASS'})
    result={'classification':'One adaptive frozen-component composition; references retained, no fresh pair or general release',
            'rows':rows,'comparisons':comparisons,'manifest_sha256':original.cap.kd.sha(root/'manifest.json'),
            'base_sha256':hashlib.sha256(base).hexdigest(),'base_bytes':len(base),'base_recorded_exactly_in_native_metadata':True,
            'finite_checks':'PASS','segments':report['segments'],'turns':report['turns'],'raw_capture':report['raw_capture'],
            'memory_preflight':report['memory_preflight'],'caller_seconds':report['caller_seconds'],
            'new_candidate_streams':1,'general_release':False,
            'limits':['Known fixture and adaptive composition; retained comparisons, not causal replication',
                      'Only the client base changes; server-side instruction additions remain unknown',
                      'Reported reasoning counts are observable, their causal internal allocation is not',
                      'Full physical I/O, implementation/research and coordinator cost are not metered']}
    original.cap.kd.save(root/'composition-audit.json',result)
    Path(__file__).with_name('LUNA_CODING_COMPOSED_V1_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'usage':candidate,'comparisons':comparisons,'segments':report['segments'],'checks':'PASS'}))


if __name__=='__main__':audit(sys.argv[1])
