"""Reconcile native receipts for the fresh assembled known-W50 pair."""
import json,sys
from pathlib import Path
from assembled_luna_pair import verify,sha,grade
from app_server_native import usage


def audit(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m)
    r=json.loads((root/'results.json').read_text())
    assert r['state']=='AWAITING_INDEPENDENT_AUDIT'
    rows=[]
    for arm,expected_turns in [('off',50),('on',1)]:
        path=root/arm/'receipts/run';s=json.loads((path/'status.json').read_text())
        assert s['state']=='closed' and s['model']==m['model'] and s['effort']=='high'
        assert len(s['turns'])==expected_turns and all(t['state']=='completed' for t in s['turns'])
        assert sha(path/'native-events.jsonl')==s['native_events_sha256']
        events=[json.loads(l) for l in (path/'native-events.jsonl').read_text().splitlines()]
        updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert usage(updates[-1])==s['usage']==r['rows'][arm]['usage']
        for k,n in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][n] for e in updates)==s['usage'][k]
        assert r['rows'][arm]['acks']==['ACK E%02d'%i for i in range(1,50)]
        grade(r['rows'][arm]['answer'])
        rows.append({'arm':arm,'usage':s['usage'],'turns':expected_turns,'segments':len(updates),
            'native_sha256':s['native_events_sha256'],'checks':'49 ACKs and frozen final grader PASS',
            'elapsed_seconds':r['rows'][arm]['elapsed_seconds'],
            'engine_object_io':r['rows'][arm]['engine_object_io']})
    a,b=[x['usage'] for x in rows]
    savings={k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')}
    result={'classification':'Fresh known-W50 development pair; no general capability certification',
        'rows':rows,'savings_percent':savings,
        'uncached_input_savings_percent':100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens'])),
        'meets_75_75':all(v>=75 for v in savings.values()),'meets_80_80':all(v>=80 for v in savings.values()),
        'manifest_sha256':sha(root/'manifest.json'),'general_release':False,
        'limits':['N=1 continuation pair; median equals single observation','Coding/retrieval are separate unqualified families','Same default base; native skill attached only in candidate','Object I/O not full physical/SQLite/storage/research cost','Normal Codex app delivery not tested']}
    Path(__file__).with_name('ASSEMBLED_LUNA_PAIR_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':audit(sys.argv[1])
