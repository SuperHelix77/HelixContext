"""Audit native counters/settings and publish normal finals; no inference."""
from pathlib import Path
import hashlib,json,sys
import pilot

HERE=Path(__file__).resolve().parent
FIELDS={'input_tokens':'inputTokens','output_tokens':'outputTokens','cached_input_tokens':'cachedInputTokens','reasoning_output_tokens':'reasoningOutputTokens'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def run(root):
    root=Path(root).resolve();m=read(root/'manifest.json');pilot.verify(m);r=read(root/'results.json')
    assert r['state']=='AWAITING_AUDIT' and len(r['rows'])==2
    assert r['manifest_sha256']==sha((root/'manifest.json').read_bytes())
    out=HERE/'artifacts';out.mkdir(exist_ok=False)
    rows=[];ids=set();prompt_inputs={}
    for row in r['rows']:
        arm=row['arm'];folder=root/arm;n=folder/'native';s=read(n/'status.json')
        assert s['state']=='closed' and s['model']==m['model'] and s['effort']==m['effort']
        assert s['thread_id'] not in ids;ids.add(s['thread_id'])
        assert s['effective_config_binding']['native_overrides_verified']
        assert s['effective_config_binding']['other_parsed_settings_unchanged']
        assert s['effective_config_binding']['changed_top_level_keys']==[]
        assert sha((n/'native-events.jsonl').read_bytes())==s['native_events_sha256']
        es=[json.loads(l) for l in (n/'native-events.jsonl').read_text().splitlines()]
        updates=[e['params'] for e in es if e.get('method')=='thread/tokenUsage/updated']
        assert updates and all(u['threadId']==s['thread_id'] for u in updates)
        for k,v in FIELDS.items():
            assert sum(u['tokenUsage']['last'][v] for u in updates)==row['usage'][k]
            assert updates[-1]['tokenUsage']['total'][v]==row['usage'][k]==s['usage'][k]
        req=[json.loads(l) for l in (n/'requests.jsonl').read_text().splitlines()]
        starts=[e['params'] for e in req if e.get('method')=='thread/start'];turns=[e['params'] for e in req if e.get('method')=='turn/start']
        assert len(starts)==len(turns)==1 and turns[0]['effort']=='xhigh' and turns[0]['model']==m['model']
        assert 'model_instructions_file' not in starts[0].get('config',{})
        inp=turns[0]['input'];assert len(inp)==2 and inp[1]['type']=='skill' and inp[1]['name']=='helixcontext'
        assert inp[0]['text'].endswith((folder/'prompt.txt').read_text())
        prompt_inputs[arm]=inp[0]['text'].replace((HERE/'STYLE.txt').read_text(),'').replace(str(folder/'work'),'<TASK_CWD>')
        raw=(n/'raw/raw-rollout.jsonl').read_bytes();assert sha(raw)==s['raw_capture']['sha256']
        assert s['raw_capture']['unmatched_calls']==s['raw_capture']['orphan_outputs']==[]
        metas=[json.loads(l)['payload'] for l in raw.splitlines() if json.loads(l).get('type')=='session_meta']
        assert len(metas)==1 and metas[0]['id']==s['thread_id']
        assert sha(metas[0]['base_instructions']['text'].encode())==m['base_sha256']
        finals=[(i,e['params']['item']) for i,e in enumerate(es) if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='agentMessage' and e['params']['item'].get('phase')=='final_answer']
        assert len(finals)==1 and finals[0][1]['text']==row['answer']==(n/'turn-1-answer.txt').read_text()
        commands=[]
        for i,e in enumerate(es):
            it=e.get('params',{}).get('item',{})
            if e.get('method')=='item/completed' and it.get('type')=='commandExecution':
                assert i<finals[0][0]
                output=it.get('aggregatedOutput') or ''
                commands.append({'command':it['command'],'exit_code':it['exitCode'],'output':output,'output_bytes':len(output.encode()),'output_sha256':sha(output.encode())})
        dst=out/arm;dst.mkdir()
        (dst/'final-answer.md').write_text(row['answer'])
        save(dst/'commands.json',commands)
        save(dst/'segments.json',[u['tokenUsage']['last'] for u in updates])
        extras=[]
        for name in row['extra_files']:
            p=folder/'work'/name
            if p.suffix=='.py':
                target=dst/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());extras.append(name)
        mem=read(folder/'memory/receipt.json')
        rows.append({'arm':arm,'model':s['model'],'effort':s['effort'],'thread_id':s['thread_id'],'usage':row['usage'],'uncached_input':row['usage']['input_tokens']-row['usage']['cached_input_tokens'],'other_output':row['usage']['output_tokens']-row['usage']['reasoning_output_tokens'],'segments':len(updates),'model_turns':len(turns),'shell_commands':len(commands),'nonzero_command_exits':sum(c['exit_code']!=0 for c in commands),'tool_return_bytes':sum(c['output_bytes'] for c in commands),'elapsed_seconds':row['elapsed_seconds'],'native_events_sha256':s['native_events_sha256'],'raw_sha256':sha(raw),'raw_bytes':len(raw),'final_sha256':sha(row['answer'].encode()),'native_final_after_tools':True,'base_config_effort_source_unchanged':True,'extra_python_files':extras,'memory_seconds':mem['elapsed_seconds'],'memory_raw_bytes':mem['raw_bytes']})
    assert prompt_inputs['off']==prompt_inputs['on'],'Unexpected native prompt difference'
    by={x['arm']:x for x in rows}
    def value(arm,key):return by[arm]['usage'][key] if key in FIELDS else by[arm][key]
    savings={k:100*(1-value('on',k)/value('off',k)) if value('off',k)>0 else None for k in [*FIELDS,'uncached_input','other_output']}
    report={'classification':'N=1 synthetic two-proposal review, reasoning-style diagnostic; not release/parity evidence','model':m['model'],'effort':m['effort'],'manifest_sha256':sha((root/'manifest.json').read_bytes()),'prereg_commit':'0afc80c','rows':rows,'savings_percent':savings,'native_input_only_style_changed':True,'all_attempts_usage':{k:sum(x['usage'][k] for x in rows) for k in FIELDS},'successful_preparation_seconds':m['preparation_seconds'],'offline_preparation_attempts':2,'included_quota_saving':None,'complete_physical_io':None,'semantic_review':'PENDING_EXPLICIT_REVIEW','deployment':False,'full_goal_achieved':False}
    save(HERE/'RESULT.json',report)
    print(json.dumps({'savings':savings,'rows':[{k:r[k] for k in ['arm','usage','segments','shell_commands']} for r in rows]},indent=2))

if __name__=='__main__':run(sys.argv[1])
