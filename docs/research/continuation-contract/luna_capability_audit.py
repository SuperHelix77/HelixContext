"""Reconcile the frozen Luna capability regression streams and paired costs."""
import json
import sys
from pathlib import Path
import luna_capability_pair as bench
from app_server_native import usage


def audit(root, out):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());bench.verify(m)
    result=json.loads((root/'results.json').read_text())
    assert result['state']=='AWAITING_TRACE_AUDIT' and len(result['rows'])==6
    rows=[]
    for case,arm in m['order']:
        p=root/(case+'-'+arm+'-run');s=json.loads((p/'status.json').read_text())
        assert s['state']=='closed' and s['model']==m['model'] and s['effort']=='high'
        assert bench.kd.sha(p/'native-events.jsonl')==s['native_events_sha256']
        assert bench.kd.sha(p/'events.jsonl')==s['events_sha256']
        events=[json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
        steps=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert all(e['params']['threadId']==s['thread_id'] for e in steps)
        assert usage(steps[-1])==s['usage']
        for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in steps)==s['usage'][key]
        inp=json.loads((p/'turn-1-input.json').read_text());assert inp['effort']=='high'
        other='helix' if arm=='default' else 'default'
        assert inp['input'][0]['text']==(root/case/other/'prompt.txt').read_text()
        assert len([i for i in inp['input'] if i['type']=='skill'])==(1 if arm=='helix' else 0)
        req=[json.loads(l) for l in (p/'requests.jsonl').read_text().splitlines()]
        start=next(x['params'] for x in req if x.get('method')=='thread/start')
        assert start['config'].get('model_instructions_file')==(m['kernel'] if arm=='helix' else None)
        original=next(r for r in result['rows'] if (r['case'],r['arm'])==(case,arm))
        answer=(p/'turn-1-answer.txt').read_text();assert answer==original['answer']
        assert s['usage']==original['usage']
        # Exact final data and caller-run mathematical oracle, not just a model PASS.
        checks=bench.grade(root,case,root/case/arm,answer)
        commands=[e['params']['item'] for e in events if e.get('method')=='item/completed' and e['params']['item'].get('type')=='commandExecution']
        if case=='cold':
            assert any('history.json' in c['command'] and c.get('exitCode')==0 for c in commands),'No observed successful cold source access'
        rows.append({'case':case,'arm':arm,'usage':s['usage'],'segments':len(steps),
            'recorded_commands':len(commands),'checks':checks,'native_sha256':s['native_events_sha256'],
            'command_hashes':[bench.kd.research_session.sha(c['command'].encode()) for c in commands]})
        bench.kd.save(root/(case+'-'+arm+'-hud.json'),{**s,'state':'completed','runner':'app-server','source_status_sha256':bench.kd.sha(p/'status.json')})
    pairs=[]
    for case in ('coding','selection','cold'):
        a=next(r['usage'] for r in rows if r['case']==case and r['arm']=='default')
        b=next(r['usage'] for r in rows if r['case']==case and r['arm']=='helix')
        pairs.append({'case':case,'savings_percent':{k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')},
            'uncached_savings_percent':100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens']))})
    data={'classification':'Three development task pairs; exact behavioral gates passed; not general parity',
        'rows':rows,'pairs':pairs,'manifest_sha256':bench.kd.sha(root/'manifest.json'),
        'limits':m['limits']+['Product base/skill comparison; W50 renderer not applicable.',
                             'Same native High tools; no model retries. Caller audit costs additional.',
                             'Command count does not establish complete tool coverage; manual trace audit required.']}
    bench.kd.save(Path(out),data);print(json.dumps({'pairs':pairs,'rows':[{k:r[k] for k in ('case','arm','usage','segments','recorded_commands')} for r in rows]},indent=2))


if __name__=='__main__':audit(*sys.argv[1:])
