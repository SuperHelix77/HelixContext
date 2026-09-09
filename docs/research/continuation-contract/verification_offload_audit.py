"""Offline scope/cost falsifier for replacing generated receipt verification."""
import hashlib,json,shlex,subprocess,sys,tempfile
from pathlib import Path
import tiktoken

def run(root,out):
 root=Path(root);p=root/'candidate/on/receipts/run';status=json.loads((p/'status.json').read_text());raw=(p/'events.jsonl').read_bytes();assert hashlib.sha256(raw).hexdigest()==status['events_sha256']
 es=[json.loads(l) for l in raw.splitlines()];commands=[e['item']['command'] for e in es if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'];cmd=next(c for c in commands if 'identity sentinel' in c)
 body=shlex.split(cmd)[-1].split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
 start=body.index('ns={};exec(');end=body.index('for p,b in protected.items():')
 semantic=body[start:end];standalone='from pathlib import Path\n'+semantic+'\nassert cases==11\nprint(cases)\n'
 with tempfile.TemporaryDirectory(prefix='helix-semantic-slice-') as tmp:
  d=Path(tmp);(d/'proposal.py').write_bytes((root/'candidate/on/proposal.py').read_bytes());(d/'probe.py').write_text(standalone)
  r=subprocess.run([sys.executable,'-B','probe.py'],cwd=d,capture_output=True,text=True,timeout=30);assert r.returncode==0 and r.stdout.strip()=='11'
 enc=tiktoken.get_encoding('o200k_base');count=lambda s:len(enc.encode(s))
 paired=json.loads((root/'results.json').read_text());steps=paired['audit']['on']['segments'];native=paired['rows']['off']['usage'];assert len(steps)==4
 result={'classification':'Observed extraction/replay and tokenizer proxies; conditional trajectory arithmetic, not native counterfactual','native_calls':0,'events_sha256':hashlib.sha256(raw).hexdigest(),'original_command_sha256':hashlib.sha256(cmd.encode()).hexdigest(),'semantic_slice_sha256':hashlib.sha256(semantic.encode()).hexdigest(),'semantic_slice_cases_passed':11,'proxy_o200k_tokens':{'full_python_body':count(body),'retained_standalone_semantic_code':count(standalone),'removed_byte_regions':count(body[:start]+body[end:]),'warning':'Not native token attribution; separately tokenized regions need not add; native segment includes reasoning/other output.'},'conditional':{'warning':'Assume surviving segment costs unchanged. Safe removal and unchanged costs unproven. Not a lower bound.','native_80_budgets':{'input':native['input_tokens']*.2,'output':native['output_tokens']*.2},'remove_entire_combined_verification_and_semantic_segment':{'input':sum(s['inputTokens'] for i,s in enumerate(steps) if i!=2),'output':sum(s['outputTokens'] for i,s in enumerate(steps) if i!=2)},'retain_final_segment_only':steps[-1]},'decision':'Do not launch hash-verification-only 80/80 benchmark. It cannot remove needed semantic probes or repeated task context by itself.'}
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run(*sys.argv[1:])
