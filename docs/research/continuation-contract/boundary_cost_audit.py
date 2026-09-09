"""Read-only frozen safety-trace accounting; no counterfactual native claims."""
import hashlib,json,sys
from pathlib import Path
import tiktoken
ENC=tiktoken.get_encoding('o200k_base')
def measure(s):return {'bytes':len(s.encode()),'proxy_tokens':len(ENC.encode(s))}
def run(root,out):
    root=Path(root);p=root/'on/receipts/run';status=json.loads((p/'status.json').read_text())
    for f,k in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:assert hashlib.sha256((p/f).read_bytes()).hexdigest()==status[k]
    events=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
    cmds=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'];assert len(cmds)==4
    labels=['fixed apply/check','evidence path listing','snapshot and provenance inspection','new semantic tests plus stdout retrieval']
    rows=[{'index':i+1,'classification':labels[i],'command':measure(c['command']),'output':measure(c['aggregated_output'])} for i,c in enumerate(cmds)]
    wire=[json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
    steps=[];prev=None
    for e in wire:
        if e.get('method')!='thread/tokenUsage/updated' or e['params']['threadId']!=status['thread_id']:continue
        u=e['params']['tokenUsage']
        if u['total']==prev:continue
        steps.append(u['last']);prev=u['total']
    for field,key in [('inputTokens','input_tokens'),('outputTokens','output_tokens')]:assert sum(s[field] for s in steps)==status['usage'][key]
    assert len(steps)==5
    dup={}
    for name,rel in [('source','proposal.py'),('contract','CONTRACT.md')]:
        text=(root/'on'/rel).read_text();dup[name]={'in_initial_prompt':text in (p/'prompt.txt').read_text(),'in_inspection_output':text in cmds[2]['aggregated_output'],**measure(text)}
    retain=[steps[i] for i in [0,3,4]]
    total=status['usage']['input_tokens'];hyp=sum(s['inputTokens'] for s in retain)
    result={'classification':'OBSERVED counters and proxies; conditional trajectory arithmetic only','native_usage':status['usage'],'segments':steps,'commands':rows,'duplicates':dup,
      'conditional_drop_two_navigation_segments':{'retained_input':hyp,'removed_input_percent':100*(1-hyp/total),'assumption':'Delete the two navigation-producing model segments; retain other segment costs unchanged. Neither safe removal nor unchanged trajectory established.'},
      'output_80_percent_allowance_relative_to_this_safety_run':status['usage']['output_tokens']*.2,
      'proxy_warning':'o200k_base counts are not native output attribution, additive token bills, or model lower bounds.',
      'no_new_native_calls':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run(*sys.argv[1:])
