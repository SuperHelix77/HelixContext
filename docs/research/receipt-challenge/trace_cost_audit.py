"""Read-only cost anatomy of the stopped pilot. Proxies never become native bills."""
import hashlib
import json
from pathlib import Path
import shlex
import sys
import tiktoken

ENC=tiktoken.get_encoding('o200k_base')
def sha(b):return hashlib.sha256(b).hexdigest()
def measure(text):return {'utf8_bytes':len(text.encode()),'o200k_proxy_tokens':len(ENC.encode(text))}


def audit(root):
    root=Path(root);run=root/'helix_valid/receipts/run';cwd=root/'helix_valid/on'
    status=json.loads((run/'status.json').read_text());start=json.loads((run/'thread-start.json').read_text())
    for filename,field in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:
        assert sha((run/filename).read_bytes())==status[field]
    wire=[json.loads(x) for x in (run/'native-events.jsonl').read_text().splitlines()]
    steps=[];previous=None
    for event in wire:
        if event.get('method')!='thread/tokenUsage/updated':continue
        if event['params']['threadId']!=status['thread_id']:continue
        usage=event['params']['tokenUsage'];total=usage['total']
        if total==previous:continue
        last=usage['last'];steps.append({k:last[k] for k in ('inputTokens','outputTokens','cachedInputTokens','reasoningOutputTokens')});previous=total
    assert sum(s['inputTokens'] for s in steps)==status['usage']['input_tokens']
    assert sum(s['outputTokens'] for s in steps)==status['usage']['output_tokens']
    events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
    commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    assert len(commands)==3,'Re-audit manual classifications if trace changes'
    rows=[]
    labels=['task-directory discovery','exact evidence re-read and hash display','mixed receipt binding and NEW semantic tests']
    for index,item in enumerate(commands):
        text=item['command'];row={'index':index+1,'classification':labels[index],'command':measure(text),'recorded_output':measure(item['aggregated_output']),'exit_code':item['exit_code'],'command_sha256':sha(text.encode())}
        if index==2:
            shell=shlex.split(text)[-1]
            # Exact textual boundary visible in this frozen command; not a general parser.
            marker="ns={}; exec(compile(Path('proposed.py')"
            assert shell.count(marker)==1
            left,right=shell.split(marker)
            row['mechanical_prefix']=measure(left)
            row['semantic_suffix']=measure(marker+right)
            row['partition_note']='String boundary only; wrapper included; tokenizer pieces not additive to native usage.'
        rows.append(row)
    prompt=(run/'prompt.txt').read_text()
    supplied={n:measure((cwd/n).read_text()) for n in ('CONTRACT.md','proposed.py','mechanical_checker.py','receipt.json')}
    raw2=commands[1]['aggregated_output']
    duplicates={n:{**measure((cwd/n).read_text()),'in_prompt':(cwd/n).read_text() in prompt,'in_second_output':(cwd/n).read_text() in raw2} for n in ('CONTRACT.md','proposed.py')}
    instruction_files=[]
    for name in start.get('instructionSources',[]):
        p=Path(name)
        instruction_files.append({'name':p.name,'scope':'global' if '.codex' in p.parts else 'task','current_snapshot_sha256':sha(p.read_bytes()),**measure(p.read_text()),'historical_content_binding':'UNAVAILABLE; source path alone is not a historical content hash'})
    requests=[json.loads(x) for x in (run/'requests.jsonl').read_text().splitlines()]
    request=next(x for x in requests if x.get('method')=='thread/start')
    cap=request['params']['config']['skills.max_context_tokens']
    skill=cwd/'.agents/skills/helixcontext/SKILL.md'
    assert sha(skill.read_bytes())==status['registration']['skill_sha256']
    return {'classification':'OBSERVED native totals + tokenizer proxies + conditional unchanged-trajectory ceiling',
        'native_usage':status['usage'],'segments':steps,'commands':rows,'prompt':measure(prompt),
        'supplied_files':supplied,'exact_duplicate_content':duplicates,'instruction_sources':instruction_files,
        'attached_skill':{**measure(skill.read_text()),'sha256':sha(skill.read_bytes())},
        'requested_catalog_cap_tokens':cap,'conditional_catalog_only_ceiling_tokens':cap*len(steps),
        'conditional_catalog_only_ceiling_percent':100*cap*len(steps)/status['usage']['input_tokens'],
        'full_rendered_prompt_available':False,'platform_or_helix_residual_token_attribution':None,
        'native_events_sha256':status['native_events_sha256'],'audit_script_sha256':sha(Path(__file__).read_bytes()),
        'limits':['Catalog cap applies only if installed runtime honors documented semantics; requested setting is observed, rendered catalog is not.',
                  'Unchanged-trajectory arithmetic is not a counterfactual model measurement.',
                  'No private reasoning content analyzed; reported subset counters only.',
                  'No new model call; no capability removal or runtime config change.']}

if __name__=='__main__':
    result=audit(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
