"""Independent native receipt reconciliation; no new inference."""
import json, statistics, sys
from pathlib import Path
from assembled_luna_pair import verify, sha
from app_server_native import usage
from luna_semantic_safety_pair import CASES, check, parse
from policy_realization import realize
import hashlib


def audit(root, output_name='LUNA_SEMANTIC_SAFETY_RESULT.json'):
    root = Path(root)
    manifest = json.loads((root/'manifest.json').read_text()); verify(manifest)
    result = json.loads((root/'results.json').read_text())
    assert result['state'] in ('AWAITING_INDEPENDENT_AUDIT','STOPPED_PENDING_AUDIT')
    incomplete=[]
    for case,arm in manifest['order']:
        if any(r['case']==case and r['arm']==arm for r in result['rows']):continue
        path=root/case/arm/'receipts/run'
        if not (path/'status.json').exists():continue
        status=json.loads((path/'status.json').read_text())
        assert sha(path/'native-events.jsonl')==status['native_events_sha256']
        events=[json.loads(l) for l in (path/'native-events.jsonl').read_text().splitlines()]
        updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert usage(updates[-1])==status['usage']
        answers=[parse(p.read_text()) for p in sorted(path.glob('turn-*-answer.txt'))]
        failures=[]
        for index,answer in enumerate(answers):
            try:check(answer,case!='unsupported_initial' and index==0)
            except AssertionError:failures.append({'turn':index+1,'answer':answer})
        assert failures, 'Stopped stream requires separate audit'
        incomplete.append({'case':case,'arm':arm,'usage':status['usage'],'native_sha256':status['native_events_sha256'],'failures':failures})
    rows = []
    for row in result['rows']:
        path = root/row['case']/row['arm']/'receipts/run'
        status = json.loads((path/'status.json').read_text())
        expected = 2 if row['case'] == 'changed_after_selection' else 1
        assert status['state'] == 'closed' and status['model'] == manifest['model'] and status['effort'] == 'high'
        assert len(status['turns']) == expected and all(t['state']=='completed' for t in status['turns'])
        assert sha(path/'native-events.jsonl') == status['native_events_sha256']
        events = [json.loads(l) for l in (path/'native-events.jsonl').read_text().splitlines()]
        updates = [e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert usage(updates[-1]) == status['usage'] == row['usage']
        for key, native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates) == row['usage'][key]
        for index, answer in enumerate(row['answers']):
            allowed = row['case'] != 'unsupported_initial' and index == 0
            check(answer, allowed)
            if not allowed:
                assert 'ticket' in answer['explanation'].lower(), 'Manual causal explanation review required'
            # Ordinary semantic answers must match the retained native output.
            if row['arm']=='off' or row['case']=='unsupported_initial' or index>0:
                assert parse((path/f'turn-{index+1}-answer.txt').read_text()) == answer
            else:
                spec=json.loads((root/(row['case']+'.json')).read_text())
                raw=b'\n'.join(json.dumps({'event':e}).encode() for e in spec['initial'])
                selection=parse((path/'turn-1-answer.txt').read_text())
                request={k:spec['request'][k] for k in ('subject','distinct_approvers','approver_group')}
                assert realize(selection,raw,hashlib.sha256(raw).hexdigest(),request)['answer']==answer
        commands = [e for e in events if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='commandExecution']
        hooks=[e for e in events if e.get('method')=='hook/completed' and e.get('params',{}).get('run',{}).get('eventName')=='preToolUse']
        rows.append({**row, 'segments':len(updates),'commands':len(commands),'completed_pretool_hooks':len(hooks),'command_count_scope':'completed commandExecution items only; not proof of zero tool attempts', 'native_sha256':status['native_events_sha256'],'elapsed_seconds':status['elapsed_seconds']})
    paired=[]
    for case in CASES:
        if sum(r['case']==case for r in rows)!=2:continue
        a,b=[next(r['usage'] for r in rows if r['case']==case and r['arm']==arm) for arm in ('off','on')]
        paired.append({'case':case, 'input':100*(1-b['input_tokens']/a['input_tokens']), 'output':100*(1-b['output_tokens']/a['output_tokens']), 'uncached':100*(1-(b['input_tokens']-b['cached_input_tokens'])/(a['input_tokens']-a['cached_input_tokens']))})
    report={'classification':'Partial semantic safety suite stopped on native control failure; not W50 or general capability qualification' if incomplete else 'Three fresh compact semantic safety pairs; not general capability qualification','checks':'STOPPED_CONTROL_FAILURE' if incomplete else 'PASS', 'manifest_sha256':sha(root/'manifest.json'), 'rows':rows, 'failed_streams':incomplete,'completed_pairs':len(paired), 'paired_savings_percent':paired, 'median_savings_percent':None if incomplete else {k:statistics.median(r[k] for r in paired) for k in ('input','output','uncached')}, 'general_release':False, 'limits':['One observation per case; no statistical parity claim','Caller selects supported path from explicit fixture state; no general automatic semantic router tested','Changed-policy reentry explicitly requested by caller; autonomous change detection not established','Engine setup, storage and physical I/O not completely instrumented; token savings are not total cost savings','Same default base and High; candidate skill attachment is part of measured treatment','No new long-horizon pair; earlier W50 result remains separate']}
    report['all_attempt_usage']={k:sum(r['usage'][k] for r in rows+incomplete) for k in ('input_tokens','output_tokens','cached_input_tokens','reasoning_output_tokens')}
    report['ratio_of_totals_savings_percent']=None
    if not incomplete:
        totals={arm:{k:sum(r['usage'][k] for r in rows if r['arm']==arm) for k in ('input_tokens','output_tokens','cached_input_tokens')} for arm in ('off','on')}
        report['ratio_of_totals_savings_percent']={k:100*(1-totals['on'][k]/totals['off'][k]) for k in ('input_tokens','output_tokens')}
    output=Path(__file__).with_name(output_name)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('checks','paired_savings_percent','median_savings_percent')},indent=2))


if __name__=='__main__': audit(*sys.argv[1:])
