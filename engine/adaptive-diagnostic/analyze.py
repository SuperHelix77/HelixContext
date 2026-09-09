"""Reuse completed receipts; this script never launches a model."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'engine/adaptive-diagnostic'
SOURCES={'typed_terminal':'engine/native-pilots/pilot-v2/results.json','exact_renderer':'engine/render-pilot/results.json','literal_query_v1':'engine/query-pilot-v1/results.json','literal_query_v2':'engine/query-pilot-v2/results.json'}

def main():
 rows=[];sources=[]
 for concept,path in SOURCES.items():
  p=ROOT/path
  if not p.exists():continue
  raw=p.read_bytes();sources.append({'concept':concept,'path':path,'sha256':hashlib.sha256(raw).hexdigest()})
  data=json.loads(raw)
  for model in sorted({r['model'] for r in data['rows']}):
   pair={r['arm']:r for r in data['rows'] if r['model']==model}
   off,on=pair['off'],pair['on']
   rows.append({'model':model,'concept':concept,'input_off':off['usage']['input_tokens'],'input_on':on['usage']['input_tokens'],'output_off':off['usage']['output_tokens'],'output_on':on['usage']['output_tokens'],'input_saved':1-on['usage']['input_tokens']/off['usage']['input_tokens'],'output_saved':1-on['usage']['output_tokens']/off['usage']['output_tokens'],'quality_scope':'single paired exposed task, exact-answer/artifact and source-integrity only'})
 variability=[]
 for model in sorted({r['model'] for r in rows}):
  eligible=[r for r in rows if r['model']==model and r['concept']!='exact_renderer']
  variability.append({'model':model,'same_task_control_count':len(eligible),'input_min':min(r['input_off'] for r in eligible),'input_max':max(r['input_off'] for r in eligible),'output_min':min(r['output_off'] for r in eligible),'output_max':max(r['output_off'] for r in eligible),'warning':'Controls from different development runs, not randomized contemporaneous replicates; range shows observed variability, not a confidence interval or a causal noise estimate.'})
 OUT.mkdir(exist_ok=True)
 (OUT/'results.json').write_text(json.dumps({'sources':sources,'comparisons':rows,'baseline_variability':variability,'new_model_calls':0},indent=2)+'\n')
 print(json.dumps(variability,indent=2))

if __name__=='__main__':main()
