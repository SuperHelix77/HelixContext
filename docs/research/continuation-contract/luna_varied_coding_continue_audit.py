"""Audit completed native turns and the one explicit setup-registration recovery."""
import hashlib,json
from pathlib import Path
from statistics import median
import sys
import luna_varied_coding_v1 as v1
from project_registration_preflight import registration_delta


def audit(root):
    root=Path(root).resolve();m=json.loads((root/'continuation-manifest.json').read_text());v1.verify(m)
    result=json.loads((root/'continuation-results.json').read_text());assert result['state']=='AWAITING_CONTINUATION_AUDIT'
    rows=[]
    for row in result['rows']:
        case,arm=row['case'],row['arm'];run=root/case/(arm+'-run');s=json.loads((run/'status.json').read_text())
        assert s['model']==m['model'] and s['effort']=='high' and all(t['state']=='completed' for t in s['turns'])
        if row.get('recovered_guard'):
            recovery=json.loads((root/'recovery-result.json').read_text())
            assert case=='intervals' and arm=='on' and s['state']=='failed' and len(s['turns'])==1
            assert v1.sha(run/'status.json')==recovery['original_status_sha256']
            registration=registration_delta((run/'config.initial.private.toml').read_bytes(),(run/'config.final.private.toml').read_bytes(),root/case/arm)
            assert registration==recovery['registration_delta'] and registration['added_trusted_marker']
            assert s['raw_capture']['calls']==0 and recovery['model_calls_added']==0
        else:
            assert s['state']=='closed'
            binding=s['effective_config_binding'];assert binding['other_parsed_settings_unchanged'] and binding['native_overrides_verified']
            assert v1.sha(run/'config.initial.private.toml')==binding['initial_sha256'] and v1.sha(run/'config.final.private.toml')==binding['final_sha256']
        wire=(run/'native-events.jsonl').read_bytes();assert hashlib.sha256(wire).hexdigest()==s['native_events_sha256']
        events=[json.loads(l) for l in wire.splitlines()];updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert v1.usage(updates[-1])==s['usage']==row['usage']
        for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates)==s['usage'][key]
        raw=(run/'raw/raw-rollout.jsonl').read_bytes();idx=json.loads((run/'raw/raw-tool-index.json').read_text())
        assert hashlib.sha256(raw).hexdigest()==idx['sha256']==s['raw_capture']['sha256']
        for x in idx['records']:assert hashlib.sha256(raw[x['start']:x['end']]).hexdigest()==x['line_sha256']
        meta=next(json.loads(l)['payload'] for l in raw.splitlines() if json.loads(l).get('type')=='session_meta');base=meta['base_instructions']['text'].encode()
        if arm=='on':
            assert base==v1.BASE.read_bytes()[:-1] and meta['base_instructions']['provenance']['type']=='custom'
            if row['finite_checks']=='PASS':assert v1.source(row['turns'][-1]['answer'])==(root/case/arm/'solution.py').read_bytes()
        else:assert hashlib.sha256(base).hexdigest()==v1.DEFAULT_HASH
        checks=v1.grade(case,root/case/arm,root/case/(arm+'-continuation-audit-check.json'))
        assert (checks['exit_code']==0)==(row['finite_checks']=='PASS')
        cwd=root/case/arm
        import subprocess
        assert Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=cwd,text=True).strip()).resolve()==cwd
        rows.append({'case':case,'arm':arm,'usage':s['usage'],'native_sha256':s['native_events_sha256'],'raw_sha256':idx['sha256'],
                     'raw_bytes':idx['bytes'],'raw_tool_calls':idx['calls'],'segments':len(updates),'turns':len(s['turns']),
                     'source_sha256':v1.sha(cwd/'solution.py'),'finite_checks':row['finite_checks'],'checks':checks.get('checks'),
                     'elapsed_seconds':s['elapsed_seconds'],'original_wrapper_state':s['state'],'configuration_audit_amended':bool(row.get('recovered_guard'))})
    pairs=[]
    for case in m['cases']:
        a=next(r for r in rows if r['case']==case and r['arm']=='off');b=next(r for r in rows if r['case']==case and r['arm']=='on')
        savings={k:100*(1-b['usage'][k]/a['usage'][k]) for k in ('input_tokens','output_tokens')}
        savings['uncached_input_tokens']=100*(1-(b['usage']['input_tokens']-b['usage']['cached_input_tokens'])/(a['usage']['input_tokens']-a['usage']['cached_input_tokens']))
        pairs.append({'case':case,'savings_percent':savings,'finite_checks':'PASS' if a['finite_checks']==b['finite_checks']=='PASS' else 'FAIL',
                      'meets_75_75':min(savings['input_tokens'],savings['output_tokens'])>=75,'meets_80_80':min(savings['input_tokens'],savings['output_tokens'])>=80})
    report={'classification':result['classification'],'manifest_sha256':v1.sha(root/'continuation-manifest.json'),'rows':rows,'pairs':pairs,
            'median_savings_percent':{k:median(p['savings_percent'][k] for p in pairs) for k in pairs[0]['savings_percent']},
            'N':3,'finite_checks':'PASS' if all(p['finite_checks']=='PASS' for p in pairs) else 'FAIL','general_release':False,
            'limits':m['limits']+['First candidate has explicit post-hoc registration audit; not untouched preregistration','V1 scope-confounded results and V2 interruption remain separately charged']}
    v1.save(root/'continuation-audit.json',report);v1.save(v1.HERE/'LUNA_VARIED_CODING_CONTINUATION_RESULT.json',report)
    print(json.dumps({'pairs':pairs,'median':report['median_savings_percent']}))


if __name__=='__main__':audit(sys.argv[1])
