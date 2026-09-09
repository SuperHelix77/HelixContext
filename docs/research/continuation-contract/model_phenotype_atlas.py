"""Visible activity association, never hidden cognition attribution."""
import collections,hashlib,json,re,sys
from pathlib import Path
LABELS=('semantic_choice','evidence_acquisition','mechanical_verification','state_transition','serialization_reporting')
def sha(b):return hashlib.sha256(b).hexdigest()
def tags(item):
 kind=item.get('type');labels=set()
 if kind=='commandExecution':
  cmd=item.get('command','')
  if re.search(r'\b(cat|sed|head|tail|rg|find|ls|pwd)\b|read_text|read_bytes|json\.load',cmd):labels.add('evidence_acquisition')
  if re.search(r'sha256|hashlib|\b(cp|mkdir|pytest|unittest)\b|python(?:3)?\s+\S*(?:check|supplemental)\.py|compile\(',cmd):labels.add('mechanical_verification')
  if re.search(r'activate|register|ledger|remember|recall',cmd):labels.add('state_transition')
  if re.search(r'\bassert\b|def test_|class Queue',cmd):labels.add('semantic_choice') # possible novel probe, not known reasoning attribution
 if kind=='fileChange':labels.add('semantic_choice')
 if kind=='agentMessage':
  text=item.get('text','').strip()
  if re.fullmatch(r'ACK [EL]\d+',text):labels.add('state_transition')
  elif item.get('phase')=='final_answer':labels.update(('semantic_choice','serialization_reporting'))
  elif re.search(r'register|bookkeeping|memory|skill',text,re.I):labels.add('state_transition')
 return labels

def run(base,out):
 base=Path(base);rows=[];excluded=[]
 for p in sorted(base.glob('*/**/native-events.jsonl')):
  sp=p.with_name('status.json')
  if not sp.exists():continue
  s=json.loads(sp.read_text())
  if s.get('model') not in ('gpt-5.6-sol','gpt-5.6-luna','gpt-6-astra'):continue
  if s.get('state') not in ('completed','closed'):excluded.append(str(p.relative_to(base)));continue
  raw=p.read_bytes()
  if sha(raw)!=s.get('native_events_sha256'):raise ValueError('native hash mismatch '+str(p))
  thread=s.get('thread_id');pending=set();items=[];previous=None;segments=[]
  for e in map(json.loads,raw.splitlines()):
   par=e.get('params',{})
   if par.get('threadId')!=thread:continue
   if e.get('method')=='item/completed':
    item=par.get('item',{});kind=item.get('type')
    if kind=='reasoning':continue # never inspect private reasoning content
    pending|=tags(item)
    if kind in ('commandExecution','agentMessage','fileChange'):items.append({'type':kind,'phase':item.get('phase'),'content_sha256':sha(json.dumps(item,sort_keys=True).encode())})
   if e.get('method')=='hook/completed':items.append({'type':'hook','event':par.get('run',{}).get('eventName')})
   if e.get('method')=='thread/tokenUsage/updated':
    u=par['tokenUsage'];total=u['total']
    if total==previous:continue
    previous=total;segments.append({'index':len(segments)+1,'usage':u['last'],'visible_activity_tags':sorted(pending),'mixed':len(pending)>1,'items':items});pending=set();items=[]
  for field,k in [('inputTokens','input_tokens'),('outputTokens','output_tokens'),('cachedInputTokens','cached_input_tokens'),('reasoningOutputTokens','reasoning_output_tokens')]:assert sum(x['usage'][field] for x in segments)==s['usage'][k],str(p)
  rows.append({'path':str(p.relative_to(base)),'model':s['model'],'native_sha256':sha(raw),'usage':s['usage'],'segments':segments})
 summary={}
 for model in ('gpt-5.6-luna','gpt-5.6-sol','gpt-6-astra'):
  rr=[r for r in rows if r['model']==model];ss=[s for r in rr for s in r['segments']];total={k:sum(s['usage'][k] for s in ss) for k in ('inputTokens','outputTokens','reasoningOutputTokens')}
  shares={label:{k:100*sum(s['usage'][k] for s in ss if label in s['visible_activity_tags'])/total[k] if total[k] else None for k in ('inputTokens','outputTokens')} for label in LABELS}
  summary[model]={'streams':len(rr),'segments':len(ss),'total':total,'segment_association_percent_NONADDITIVE':shares,'mixed_segments':sum(s['mixed'] for s in ss),'unknown_segments':sum(not s['visible_activity_tags'] for s in ss),'causal_class_token_fractions':'UNKNOWN','safe_counterfactual_savings':'UNKNOWN'}
 result={'classification':'Observable segment-activity atlas; automatic heuristic annotations, not cognitive attribution','native_calls':0,'models':summary,'streams':rows,'excluded_nonterminal':excluded,'limits':['Tags describe visible activity associated with an entire segment, not tokens spent on that activity.','Tags overlap; shares must not be summed or called F_m(k).','Reasoning-output counters retained, content neither inspected nor classified.','Semantic-choice tag marks possible judgment/probe/patch/final answer, not proof of irreducible reasoning.','Different tasks, controls and adaptive candidates are mixed; model aggregates are corpus composition, not causal model phenotypes.','Omitted commands can hide activity; hooks retained and unknown counts do not imply no work.','Removing tagged segments may remove necessary reasoning or change later costs. Delta_m(k) cannot be identified observationally.']}
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':run(*sys.argv[1:])
