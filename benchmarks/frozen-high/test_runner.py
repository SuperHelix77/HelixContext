import json
from pathlib import Path
import run_benchmark as r

def test_fixtures_intact():
 assert len(r.verify_inputs()['tasks'])==3

def test_fifty_real_calls_without_future_events(tmp_path,monkeypatch):
 calls=[]
 def fake(model,cwd,prompt,out):
  history=[json.loads(x) for x in (cwd/'history.jsonl').read_text().splitlines()]
  events=[h['event'] for h in history if h['role']=='user'];turn=events[-1]['turn']
  assert len(events)==turn
  assert all(e['turn']<=turn for e in events)
  if turn<50:assert 'decide whether ORION-42 rollback' not in prompt
  if turn==50:
   assert events[0]['data']['recovery_nonce'] not in prompt
   assert len(history)==99
  answer=f'ACK E{turn:02d}'
  out.mkdir(parents=True);status={'usage':{'input_tokens':10,'output_tokens':2},'elapsed_seconds':.1,'resident_prompt_proxy_tokens':5}
  r.save(out/'status.json',status);calls.append(turn);return answer,status
 monkeypatch.setattr(r,'native',fake)
 r.run_task('astra','W','on',tmp_path/'out',tmp_path/'work')
 assert calls==list(range(1,51))
 history=[json.loads(x) for x in (tmp_path/'out/W/on/history.jsonl').read_text().splitlines()]
 assert len(history)==100
 summary=r.load(tmp_path/'out/W/on/summary.json');assert summary['turns']==50;assert summary['usage']['input_tokens']==500

def test_normal_retains_history(tmp_path,monkeypatch):
 def fake(model,cwd,prompt,out):
  history=[json.loads(x) for x in (cwd/'history.jsonl').read_text().splitlines()]
  assert history[0]['event']['data']['recovery_nonce'] in prompt
  turn=len([h for h in history if h['role']=='user']);out.mkdir(parents=True)
  s={'usage':{'input_tokens':10,'output_tokens':2},'elapsed_seconds':.1,'resident_prompt_proxy_tokens':5};r.save(out/'status.json',s);return f'ACK E{turn:02d}',s
 monkeypatch.setattr(r,'native',fake)
 r.run_task('astra','W','off',tmp_path/'out',tmp_path/'work')
 assert r.load(tmp_path/'out/W/off/summary.json')['turns']==50
