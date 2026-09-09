"""Reconcile native coding receipts, publication and exact tool evidence."""
import hashlib,json,sys
from pathlib import Path
from app_server_native import usage
from luna_coding_decision_v2 import cap,source


def audit(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());cap.verify(m)
    r=json.loads((root/'results.json').read_text());assert r['state']=='AWAITING_AUDIT'
    s=json.loads((root/'run/status.json').read_text())
    assert s['state']=='closed' and s['model']==m['model'] and s['effort']=='high'
    wire=root/'run/native-events.jsonl';assert cap.kd.sha(wire)==s['native_events_sha256']
    events=[json.loads(l) for l in wire.read_text().splitlines()]
    updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
    assert usage(updates[-1])==s['usage']==r['usage']
    for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
        assert sum(e['params']['tokenUsage']['last'][native] for e in updates)==s['usage'][key]
    for name in ('settings.json','test_allocation.py'):assert cap.kd.sha(root/'on'/name)==m['input_roots'][name]
    final=r['turns'][-1];raw_source=source(final['answer'])
    assert raw_source==(root/'on/allocation.py').read_bytes()
    assert hashlib.sha256(raw_source).hexdigest()==final['completion']['source_sha256']
    grade=json.loads((root/f'stage-{len(r["turns"])}-caller-grade.json').read_text())
    assert grade['exit_code']==0 and 'ORACLE_CASES 4433' in grade['stdout']
    raw=(root/'run/raw/raw-rollout.jsonl').read_bytes();index=json.loads((root/'run/raw/raw-tool-index.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==index['sha256']==s['raw_capture']['sha256']
    for record in index['records']:
        assert hashlib.sha256(raw[record['start']:record['end']]).hexdigest()==record['line_sha256']
    prior=Path(m['prior']);control=json.loads((prior/'coding-default-run/status.json').read_text())
    assert cap.kd.sha(prior/'coding-default-run/native-events.jsonl')==control['native_events_sha256']
    a,b=control['usage'],r['usage']
    report={'classification':'Adaptive known coding candidate; source-only output; retained earlier control; not fresh pair',
            'checks':'Public suite and 4433-case oracle PASS; exact publication and protected files PASS',
            'control_usage':a,'candidate_usage':b,'savings_percent':{k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')},
            'uncached_savings_percent':100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens'])),
            'native_sha256':s['native_events_sha256'],'source_sha256':final['completion']['source_sha256'],
            'manifest_sha256':cap.kd.sha(root/'manifest.json'),'turns':len(s['turns']),'segments':len(updates),
            'segment_usage':[u['params']['tokenUsage']['last'] for u in updates],
            'raw_capture':{k:index[k] for k in ('sha256','bytes','calls','outputs','unmatched_calls','logical_capture_read_bytes','logical_capture_write_bytes')},
            'caller_seconds':final['completion']['caller_seconds'],'engine_active':True,'general_release':False,
            'limits':['N=1 adaptive candidate, reused control; no general parity inference','Candidate durable raw capture differs from ephemeral control','Exact physical I/O and complete preprocessing/research costs not measured','Current-state checks are not hostile concurrent-writer isolation']}
    Path(__file__).with_name('LUNA_CODING_DECISION_V2_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('checks','savings_percent','uncached_savings_percent','segments','turns')}))


if __name__=='__main__':audit(sys.argv[1])
