"""Audit existing receipts only. Counterfactual arithmetic is not native evidence."""
import hashlib,json,sys
from pathlib import Path

def audit(root):
    root=Path(root); result={'classification':'OBSERVED; conditional arithmetic separately labelled','arms':{}}
    for arm in ('on','off'):
        p=root/arm/'receipts/run'; status=json.loads((p/'status.json').read_text())
        hashes={}
        for name,key in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:
            hashes[name]=hashlib.sha256((p/name).read_bytes()).hexdigest()
            assert hashes[name]==status[key],name
        events=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
        commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
        wire=[json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
        steps=[];prev=None
        for e in wire:
            if e.get('method')!='thread/tokenUsage/updated' or e['params']['threadId']!=status['thread_id']:continue
            u=e['params']['tokenUsage']
            if u['total']==prev:continue
            steps.append(u['last']);prev=u['total']
        for field,key in [('inputTokens','input_tokens'),('outputTokens','output_tokens'),('cachedInputTokens','cached_input_tokens')]:
            assert sum(s[field] for s in steps)==status['usage'][key],key
        prompt=json.loads((p/'turn-1-input.json').read_text())
        text='\n'.join(x.get('text','') for x in prompt['input'])
        duplicates={}
        for rel in ('proposal.py','CONTRACT.md','.agents/skills/helixcontext/SKILL.md','check.py','check_independence.py'):
            raw=(root/arm/rel).read_bytes();body=raw.decode()
            duplicates[rel]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'exact_in_text_prompt':body in text,'exact_in_command_outputs':[i+1 for i,c in enumerate(commands) if body in c.get('aggregated_output','')]}
        result['arms'][arm]={'usage':status['usage'],'segments':steps,'source_hashes':hashes,'file_exposure':duplicates,'commands':[{'index':i+1,'command':c['command'],'exit_code':c['exit_code'],'visible_output_bytes':len(c.get('aggregated_output','').encode())} for i,c in enumerate(commands)]}
    on=result['arms']['on'];off=result['arms']['off'];s=on['segments'];assert len(s)==4
    budgets={k:off['usage'][k]*.2 for k in ('input_tokens','output_tokens')}
    result['conditional']={'warning':'No safe-removal or unchanged-trajectory claim. These are accounting sensitivities, not measured counterfactuals or model lower bounds.', 'native_80_percent_budgets':budgets,'retain_only_semantic_probe_and_final_segments':{'input_tokens':sum(x['inputTokens'] for x in s[2:]),'output_tokens':sum(x['outputTokens'] for x in s[2:])},'two_times_observed_initial_input':2*s[0]['inputTokens'],'probe_generating_segment_output':s[2]['outputTokens'],'output_above_budget_in_probe_segment':s[2]['outputTokens']-budgets['output_tokens']}
    result['limits']=['No hidden-reasoning attribution.','Attached skill serialization not visible in text prompt; do not infer absent skill or count its double injection exactly.','Native input includes runtime context; cannot attribute its entirety to Helix bootstrap.','No added native calls.']
    return result
if __name__=='__main__':
    result=audit(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['conditional'],indent=2))
