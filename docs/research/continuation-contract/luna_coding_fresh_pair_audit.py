"""Exact fresh coding-pair audit; retained-control calculations are excluded."""
import json,hashlib,sys
from pathlib import Path
from app_server_native import usage
from luna_capability_pair import verify,kd
from luna_coding_decision_v2 import source


def audit(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m)
    r=json.loads((root/'pair-results.json').read_text());assert r['state']=='AWAITING_PAIR_AUDIT'
    rows=[]
    for arm in ('off','on'):
        run=root/('off-run' if arm=='off' else 'run');s=json.loads((run/'status.json').read_text())
        assert s['state']=='closed' and s['model']==m['model'] and s['effort']=='high'
        assert all(t['state']=='completed' for t in s['turns'])
        assert kd.sha(run/'native-events.jsonl')==s['native_events_sha256']
        events=[json.loads(l) for l in (run/'native-events.jsonl').read_text().splitlines()]
        updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert usage(updates[-1])==s['usage']==r['rows'][arm]['usage']
        for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates)==s['usage'][key]
        idx=json.loads((run/'raw/raw-tool-index.json').read_text());raw=(run/'raw/raw-rollout.jsonl').read_bytes()
        assert hashlib.sha256(raw).hexdigest()==idx['sha256']==s['raw_capture']['sha256']
        for record in idx['records']:assert hashlib.sha256(raw[record['start']:record['end']]).hexdigest()==record['line_sha256']
        spec=json.loads((root/'coding-source.json').read_text())
        for name in ('settings.json','test_allocation.py'):assert (root/arm/name).read_text()==spec['files'][name]
        assert r['rows'][arm]['checks']['stdout']=='ORACLE_CASES 4433\n'
        rows.append({'arm':arm,'usage':s['usage'],'segments':len(updates),'turns':len(s['turns']),'raw_tool_calls':idx['calls'],'unmatched_raw_calls':idx['unmatched_calls'],'source_sha256':kd.sha(root/arm/'allocation.py'),'native_sha256':s['native_events_sha256'],'raw_capture_sha256':idx['sha256'],'raw_capture_bytes':idx['bytes'],'elapsed_seconds':s['elapsed_seconds']})
    candidate=json.loads((root/'results.json').read_text());assert candidate['state']=='AWAITING_AUDIT'
    assert source(candidate['turns'][-1]['answer'])==(root/'on/allocation.py').read_bytes()
    start=json.loads((root/'run/thread-start.json').read_text());assert str(root/'on/AGENTS.md') in start['instructionSources']
    a,b=[row['usage'] for row in rows]
    savings={k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')}
    result={'classification':m['pair_classification'],'manifest_sha256':kd.sha(root/'manifest.json'),'order':m['pair_order'],'rows':rows,'savings_percent':savings,'uncached_savings_percent':100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens'])),'meets_80_80':all(v>=80 for v in savings.values()),'meets_75_75':all(v>=75 for v in savings.values()),'finite_checks':'PASS','general_release':False,'N':1,'median_scope':'One paired coding task; median equals this observation, variability unknown','limits':['Known fixture, no holdout or general capability proof','Composite product comparison: supplied source, source-only output, caller memory and checks; not mechanism isolation','Same default base/High/tools/sandbox; candidate has extra local preflight instruction','Full physical/SQLite/research costs unmetered; native token economics only']}
    Path(__file__).with_name('LUNA_CODING_FRESH_PAIR_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('savings_percent','uncached_savings_percent','meets_80_80','meets_75_75','finite_checks')}))


if __name__=='__main__':audit(sys.argv[1])
