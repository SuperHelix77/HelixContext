"""Observable first-call anatomy; native counts and text proxies remain separate."""
import hashlib,json,sys
from pathlib import Path
import tiktoken
ENC=tiktoken.get_encoding('o200k_base')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def measure(text):return {'utf8_bytes':len(text.encode()),'o200k_proxy_tokens':len(ENC.encode(text))}
def run(root,out):
 root=Path(root);result={'classification':'OBSERVED native counters, text proxies and UNKNOWN attribution; no native calls','arms':{}}
 for arm,rel in [('off','off'),('on','candidate/on')]:
  p=root/rel/'receipts/run';status=json.loads((p/'status.json').read_text());start=json.loads((p/'thread-start.json').read_text());prompt=json.loads((p/'turn-1-input.json').read_text());wire=[json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
  assert sha(p/'native-events.jsonl')==status['native_events_sha256']
  first=next(e['params']['tokenUsage']['last'] for e in wire if e.get('method')=='thread/tokenUsage/updated' and e['params']['threadId']==status['thread_id'])
  texts=[x['text'] for x in prompt['input'] if x['type']=='text'];assert len(texts)==1;text=texts[0]
  before,rest=text.split('COMPLETE CONTRACT:\n',1);contract,module=rest.split('\nEXACT PROPOSED MODULE:\n',1)
  if 'COMPLETED EVIDENCE:\n' in before:instructions,evidence=before.split('COMPLETED EVIDENCE:\n',1)
  else:instructions,evidence=before,''
  skills=[]
  for x in prompt['input']:
   if x['type']=='skill':skills.append({'path':x['path'],'sha256':sha(x['path']),**measure(Path(x['path']).read_text())})
  sources=[]
  for path in start['instructionSources']:
   f=Path(path);sources.append({'path':path,'current_sha256':sha(f),'current_mtime_ns':f.stat().st_mtime_ns,**measure(f.read_text()),'limit':'Recorded path; current bytes are not a frozen historical instruction-body receipt.'})
  row={'native_initial_input':first['inputTokens'],'native_initial_cached_subset':first['cachedInputTokens'],'native_initial_uncached':first['inputTokens']-first['cachedInputTokens'],'native_total_input':status['usage']['input_tokens'],'initial_thread_turn_count':len(start['thread']['turns']),'cli_version':start['thread']['cliVersion'],'first_text':measure(text),'text_regions':{k:measure(v) for k,v in [('task_and_orchestration',instructions),('prepared_evidence',evidence),('contract',contract),('proposed_module',module)]},'attached_skill_sources':skills,'recorded_instruction_sources':sources,'unknown_native_terms':['platform/system/developer serialization','built-in and MCP tool-schema serialization','skill catalogue injection and formatting','environment/context wrappers','tokenizer/boundary differences'],'caller_prior_conversation_turns':0,'provenance':{f:sha(p/f) for f in ('thread-start.json','turn-1-input.json','requests.jsonl','native-events.jsonl')}}
  listing=p/'skills-list.json'
  if listing.exists():
   catalog=json.loads(listing.read_text());items=[{k:x[k] for k in ('name','description','path')} for r in catalog['data'] for x in r['skills'] if x['enabled']]
   row['available_skill_catalog']={'count':len(items),**measure(json.dumps(items,ensure_ascii=False)),'limit':'Availability API rendering proxy; not evidence of injection or additive native attribution.'}
  # Deliberately DO NOT subtract proxy tokens from native input and label remainder platform.
  result['arms'][arm]=row
 control=result['arms']['off']['native_total_input'];initial=result['arms']['on']['native_initial_input']
 result['conditional_geometry']={'control_input':control,'target_80_budget':control*.2,'assumed_unavoidable_first_charge':initial,'maximum_input_saving_if_that_charge_is_unavoidable_and_everything_else_free':100*(1-initial/control),'two_equal_first_charges':2*initial,'limit':'Conditional sensitivity only; irreducibility is UNKNOWN. No empirical lower bound established.'}
 result['accounting_rule']='Proxy regions may have boundary differences and overlapping runtime representations. No additive causal decomposition or platform residual is claimed.'
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({a:{'first':r['native_initial_input'],'text':r['first_text'],'regions':r['text_regions'],'skill':r['attached_skill_sources']} for a,r in result['arms'].items()},indent=2));print(json.dumps(result['conditional_geometry']))
if __name__=='__main__':run(*sys.argv[1:])
