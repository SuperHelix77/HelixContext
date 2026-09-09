import json
import run_latent3 as r
from run_benchmark import load,save

def test_causal_latent_archive_and_integrity(tmp_path,monkeypatch):
 original=r.ROOT;spec=load(original/'protocol/latent-v1/delay-40.json');skill=(original/'iteration3/SKILL.md').read_text();calls=[]
 class Roots:
  def __truediv__(self,sub):return tmp_path/sub if sub=='latent3-runs' else original/sub
 monkeypatch.setattr(r,'ROOT',Roots());monkeypatch.setattr(r,'WORKSPACE',tmp_path)
 def fake(model,cwd,prompt,out):
  history=[json.loads(x) for x in (cwd/'history.jsonl').read_text().splitlines()];events=[h['event'] for h in history if h['role']=='user'];t=len(events)
  assert events==spec['events'][:t] and (skill in prompt)==(t==41)
  assert json.loads(prompt.split('Current event:\n')[1])==spec['events'][t-1]
  if t==2:(cwd/'history.jsonl').write_text('bad mutation')
  out.mkdir(parents=True);s={'usage':{'input_tokens':1,'output_tokens':1},'local_process_metrics':{}};save(out/'status.json',s);calls.append(t);return f'ACK L{t:02d}',s
 monkeypatch.setattr(r,'native',fake);r.run('astra','on')
 out=tmp_path/'outputs/helix-frontier/iteration3/astra/L40/on'
 assert calls==list(range(1,42)) and len((out/'history.jsonl').read_text().splitlines())==82
 checks=load(out/'integrity.json');assert checks[1]['caller_files_unchanged'] is False and sum(x['caller_files_unchanged'] for x in checks)==40
