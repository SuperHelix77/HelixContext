import json
from pathlib import Path
import run_followups as f
from run_benchmark import load,save

def test_no_future_relevance_hint(tmp_path,monkeypatch):
 calls=[]
 monkeypatch.setattr(f,'WORKSPACE',tmp_path)
 def fake(model,cwd,prompt,out):
  hist=[json.loads(l) for l in (cwd/'history.jsonl').read_text().splitlines()];turn=hist[-1]['event']['turn']
  assert len([h for h in hist if h['role']=='user'])==turn
  if turn==1:
   assert len(hist[0]['event']['data']['notes'])==96
   assert 'A new reconciliation request has arrived' not in prompt
  if turn==21:
   assert 'packing notes","notes"' not in prompt
   assert 'label_utf8_base64' in prompt
  out.mkdir(parents=True);s={'usage':{'input_tokens':10,'output_tokens':2},'local_process_metrics':{}};save(out/'status.json',s);calls.append(turn)
  return f'ACK L{turn:02d}',s
 monkeypatch.setattr(f,'native',fake)
 # Keep protocol reads frozen, redirect only per-run writes by intercepting ROOT / followup-runs.
 original_root=f.ROOT
 class Paths:
  def __truediv__(self,sub):return tmp_path/sub if sub=='followup-runs' else original_root/sub
 monkeypatch.setattr(f,'ROOT',Paths())
 f.run('astra','L20','on')
 assert calls==list(range(1,22))

def test_q2_requirement_explicit():
 spec=load(f.ROOT/'protocol/reasoning-v2.json')
 assert 'eligible and ineligible combined' in spec['task']
