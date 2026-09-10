"""Native counter closure and finite artifact/trajectory checks; no hidden reasoning."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mixed_audit_driver',HERE/'driver.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
KEYS={'input_tokens':'inputTokens','output_tokens':'outputTokens','cached_input_tokens':'cachedInputTokens','reasoning_output_tokens':'reasoningOutputTokens','cache_write_input_tokens':'cacheWriteInputTokens'}


def audit(root,out):
    root=Path(root).resolve();out=Path(out).resolve();out.mkdir(exist_ok=False)
    result=p.read(root/'results.json');m=p.read(root/'manifest.json')
    assert result['state']=='AWAITING_FINAL_SEMANTIC_AUDIT' and len(result['rows'])==2
    assert result['manifest_sha256']==p.sha(root/'manifest.json')
    metrics=p.counters();p.validate(m,metrics,True)
    rows=[]
    for row in result['rows']:
        arm=row['arm'];run=root/(arm+'-run');status=p.read(run/'status.json')
        assert status['state']=='closed' and not status['error']
        assert status['model']==m['model'] and status['effort']==m['effort']
        assert status['effective_config_binding']['other_parsed_settings_unchanged'] and status['effective_config_binding']['native_overrides_verified']
        assert status['usage']==row['usage'] and status['config_sha256']==p.sha(p.CONFIG)
        assert status['registration']['skill_sha256']==p.sha(p.SKILL)
        expected_count=50 if arm=='off' else 4
        assert len(status['turns'])==expected_count and len(row['completed_events'])==50
        assert p.read(root/arm/'history.json')==p.protocol.fixture()['events']
        assert row['restart']=='PASS'
        raw=run/'raw/raw-rollout.jsonl';native=run/'native-events.jsonl'
        assert status['native_events_sha256']==p.sha(native) and status['raw_capture']['sha256']==p.sha(raw)
        assert status['events_sha256']==p.sha(run/'events.jsonl')
        xs=[json.loads(l) for l in native.open()]
        groups=collections.defaultdict(list);previous={k:0 for k in KEYS}
        for x in xs:
            if x.get('method')=='thread/tokenUsage/updated':
                q=x['params'];assert q['threadId']==status['thread_id']
                u=q['tokenUsage']['total'];total={k:u.get(v,0) for k,v in KEYS.items()}
                assert u['totalTokens']==total['input_tokens']+total['output_tokens']
                if total==previous:continue
                delta={k:total[k]-previous[k] for k in KEYS};assert all(v>=0 for v in delta.values())
                assert delta['cached_input_tokens']<=delta['input_tokens'] and delta['reasoning_output_tokens']<=delta['output_tokens']
                groups[q['turnId']].append(delta);previous=total
        assert previous==row['usage']
        raw_usage=[]
        for line in raw.open():
            x=json.loads(line);q=x.get('payload',{})
            if x.get('type')=='event_msg' and q.get('type')=='token_count' and q.get('info'):raw_usage.append(q['info']['total_token_usage'])
        assert raw_usage and all(raw_usage[-1].get(k,0)==previous[k] for k in KEYS)
        completed=[x['params'] for x in xs if x.get('method')=='item/completed']
        calls=[q['item'] for q in completed if q['item']['type']=='commandExecution']
        finals={q['turnId']:q['item']['text'] for q in completed if q['item']['type']=='agentMessage' and q['item'].get('phase')=='final_answer'}
        assert len(finals)==expected_count
        totals={'semantic':{k:0 for k in KEYS},'passive':{k:0 for k in KEYS}}
        event_rows=[];model_index=0
        for e in row['completed_events']:
            n=int(e['event_id'][1:]);semantic=n in [12,25,38,50]
            item={'event_id':e['event_id'],'model_invoked':e['model_invoked'],'answer_sha256':p.digest(e['answer'].encode())}
            if e['model_invoked']:
                model_index+=1;tid=e['turn']['turn_id'];u=e['turn']['usage_delta']
                assert e['answer']==finals[tid]==(run/f'turn-{model_index}-answer.txt').read_text()
                assert {k:sum(s[k] for s in groups[tid]) for k in KEYS}==u
                assert status['turns'][model_index-1]['turn_id']==tid and status['turns'][model_index-1]['state']=='completed'
                for k in KEYS:totals['semantic' if semantic else 'passive'][k]+=u[k]
                item.update(usage=u,segments=len(groups[tid]),turn_id=tid)
                if semantic:(out/(arm+'-'+e['event_id']+'-final.txt')).write_bytes(e['answer'].encode())
            else:assert arm=='on' and not semantic
            if not semantic:assert e['answer']=='ACK '+e['event_id']
            elif n==12:
                review=p.read(root/(arm+'-E12-review.json'));assert review['verdict']=='PASS' and review['answer_sha256']==item['answer_sha256']
            else:
                source=root/(arm+'-'+e['event_id']+'-artifacts')
                item['grader']=p.checks.check(n,source/'planner.py',source/'plan.json' if n>=38 else None)
                (out/(arm+'-'+e['event_id']+'-planner.py')).write_bytes((source/'planner.py').read_bytes())
                if n>=38:(out/(arm+'-'+e['event_id']+'-plan.json')).write_bytes((source/'plan.json').read_bytes())
            event_rows.append(item)
        memories=[p.read(q) for q in root.glob(arm+'-E*-memory/receipt.json')]
        visible=[q for q in completed if q['item']['type'] in ['agentMessage','commandExecution','fileChange']]
        p.save(out/(arm+'-visible.json'),visible)
        rows.append({'arm':arm,'mechanical_audit':'PASS','usage':row['usage'],'uncached_input_tokens':previous['input_tokens']-previous['cached_input_tokens'],
            'model_turns':expected_count,'segments':sum(len(x) for x in groups.values()),'events':event_rows,'usage_by_event_class':totals,
            'commands':len(calls),'failed_commands':sum(x.get('exitCode') not in [0,None] for x in calls),'raw_tool_calls':status['raw_capture']['calls'],
            'tool_output_bytes':sum(len((x.get('aggregatedOutput') or '').encode()) for x in calls),
            'native_sha256':p.sha(native),'raw_sha256':p.sha(raw),'store_io':row['store_io'],'store_and_journal_disk_bytes':sum(x.stat().st_size for dirname in [arm+'-store',arm+'-dispatch'] for x in (root/dirname).rglob('*') if x.is_file()),
            'memory_calls':len(memories),'memory_seconds':sum(v['elapsed_seconds'] for v in memories),'memory_raw_bytes':sum(v['raw_bytes'] for v in memories),'scoped_memory_count':sum(len(v['scoped_memories']) for v in memories),
            'session_wall_seconds':status['elapsed_seconds'],'config_and_effort':'PASS','final_bytes_unchanged':'PASS','restart':'PASS'})
    by={r['arm']:r for r in rows}
    savings={k:100*(1-by['on']['usage'][k]/by['off']['usage'][k]) if by['off']['usage'][k] else None for k in KEYS}
    savings['uncached_input_tokens']=100*(1-by['on']['uncached_input_tokens']/by['off']['uncached_input_tokens'])
    semantic_savings={k:100*(1-by['on']['usage_by_event_class']['semantic'][k]/by['off']['usage_by_event_class']['semantic'][k]) if by['off']['usage_by_event_class']['semantic'][k] else None for k in KEYS}
    report={'schema':'helix.mixed-w50-audit.v1','model':m['model'],'effort':m['effort'],'manifest_sha256':p.sha(root/'manifest.json'),'rows':rows,'savings_percent':savings,'semantic_checkpoint_savings_percent':semantic_savings,'metrics':result['metrics'],'audit_metrics':metrics,'preflight':p.read(root/'PREFLIGHT.json'),'setup_seconds':m['preparation_seconds'],'initial_binding_bytes':m['initial_binding_bytes'],
            'scope':'One exposed four-checkpoint development workflow; finite checks not general intelligence/agentic parity. No release median or app deployment. Original complete semantic finals retained. Physical I/O and full project economics unknown.',
            'semantic_review':'PENDING source/probe/final review','release_qualified':False}
    p.save(out/'AUDIT.json',report)
    sys.path.insert(0,str(p.REPO/'engine/hud'));import pricing
    source=pricing.fetch();rates=pricing.parse(source);costs={a:pricing.estimate(by[a]['usage'],rates[m['model']]) for a in by}
    (out/'pricing-source.md').write_bytes(source)
    p.save(out/'PRICING.json',{'source':pricing.SOURCE,'checked_at_unix':time.time(),'source_sha256':p.digest(source),'rates':rates[m['model']],'api_equivalent_scenarios':costs,'savings_percent':{k:100*(1-costs['on'][k]/costs['off'][k]) for k in ['short','long']},'scope':'Dated API-equivalent, not included-plan quota or complete project ROI'})
    print(json.dumps({'audit':'PASS','savings_percent':savings,'semantic_checkpoint_savings_percent':semantic_savings,'segments':{a:by[a]['segments'] for a in by}}))
if __name__=='__main__':audit(sys.argv[1],sys.argv[2])
