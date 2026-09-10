"""Public artifact/counter/probe reproduction. Does not regenerate native calls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
HERE=Path(__file__).resolve().parent

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
 audit=json.loads((HERE/'AUDIT.json').read_text());checks=module('public_original_checks',HERE/'checks.py');gate=module('post_run_gate',HERE/'supplemental_publication_gate.py')
 review=json.loads((HERE/'SEMANTIC_REVIEW.json').read_text());assert review['arms']['on']['verdict']=='FAIL'
 for row in audit['rows']:
  arm=row['arm'];previous={k:0 for k in row['usage']}
  mapping={'input_tokens':'inputTokens','output_tokens':'outputTokens','cached_input_tokens':'cachedInputTokens','reasoning_output_tokens':'reasoningOutputTokens','cache_write_input_tokens':'cacheWriteInputTokens'}
  for line in (HERE/'artifacts'/f'{arm}-native-usage.jsonl').open():
   x=json.loads(line)['params']['tokenUsage']['total'];u={k:x.get(v,0) for k,v in mapping.items()}
   assert all(u[k]>=previous[k] for k in u);assert x['totalTokens']==u['input_tokens']+u['output_tokens'];previous=u
  assert previous==row['usage']
  for stage in [25,38,50]:
   checks.check(stage,HERE/'artifacts'/f'{arm}-E{stage}-planner.py',HERE/'artifacts'/f'{arm}-E{stage}-plan.json' if stage>=38 else None)
  outcome=gate.check(HERE/'artifacts'/f'{arm}-E50-planner.py')
  assert outcome['verdict']==('PASS' if arm=='off' else 'FAIL')
  assert len(outcome['failures'])==(0 if arm=='off' else 6)
  for event in row['events']:
   if event['event_id'] in ['E12','E25','E38','E50']:
    raw=(HERE/'artifacts'/f"{arm}-{event['event_id']}-final.txt").read_bytes();assert hashlib.sha256(raw).hexdigest()==event['answer_sha256']
 rows=json.loads((HERE/'cross-probes/RESULT.json').read_text())['rows'];results=[]
 events=json.loads((HERE/'fixture.json').read_text())['events']
 for row in rows:
  with tempfile.TemporaryDirectory() as td:
   cwd=Path(td);arm=row['tested_arm'];stage=row['stage']
   for ext,name in [('planner.py','planner.py'),('plan.json','plan.json')]:
    src=HERE/'artifacts'/f'{arm}-E{stage}-{ext}'
    if src.exists():shutil.copyfile(src,cwd/name)
   (cwd/'history.json').write_text(json.dumps(events[:stage],ensure_ascii=False))
   src=HERE/'cross-probes'/row['program'];assert hashlib.sha256(src.read_bytes()).hexdigest()==row['sha256']
   shutil.copyfile(src,cwd/'native_probe.py');r=subprocess.run([sys.executable,'-B','native_probe.py'],cwd=cwd,capture_output=True,timeout=15)
   assert r.returncode==row['exit_code'];results.append(r.returncode)
 assert len(results)==12 and results.count(0)==11
 assert gate.check(HERE/'reference.py')['verdict']=='FAIL'
 closure=HERE/'CLOSURE.json'
 if closure.exists():
  c=json.loads(closure.read_text())
  for name,h in c['sha256'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==h,name
 print(json.dumps({'verification':'PASS','expected_candidate_parity':'FAIL','cross_probe_runs':12,'expected_cross_probe_failures':1,'native_usage_and_final_hashes':'PASS','original_reference_blind_spot_reproduced':True,'new_model_calls':0}))
if __name__=='__main__':verify()
