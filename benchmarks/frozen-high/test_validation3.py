import json
import run_validation3 as v
from run_benchmark import save,load

def test_progressive_disclosure_archive_and_mutation_gate(tmp_path,monkeypatch):
 original=v.ROOT; calls=[];spec=load(original/'protocol/long-horizon-v1.json');skill=(original/'iteration3/SKILL.md').read_text()
 class Roots:
  def __truediv__(self,sub):return tmp_path/sub if sub=='validation3-runs' else original/sub
 monkeypatch.setattr(v,'ROOT',Roots());monkeypatch.setattr(v,'WORKSPACE',tmp_path)
 def fake(model,cwd,prompt,out):
  hist=[json.loads(x) for x in (cwd/'history.jsonl').read_text().splitlines()];events=[h['event'] for h in hist if h['role']=='user'];t=len(events)
  assert events==spec['events'][:t]
  assert (skill in prompt)==(t==50)
  assert json.loads(prompt.split('Current event:\n')[1])==spec['events'][t-1]
  if t==3:(cwd/'ledger.jsonl').write_text('unsolicited mutation')
  out.mkdir(parents=True);s={'usage':{'input_tokens':1,'output_tokens':1},'local_process_metrics':{}};save(out/'status.json',s);calls.append(t);return f'ACK E{t:02d}',s
 monkeypatch.setattr(v,'native',fake);v.run('astra','W','on')
 out=tmp_path/'outputs/helix-frontier/iteration3/astra/W/on'
 assert calls==list(range(1,51))
 integrity=load(out/'integrity.json');assert len(integrity)==50 and integrity[2]['caller_files_unchanged'] is False
 assert sum(x['caller_files_unchanged'] for x in integrity)==49
 history=[json.loads(x) for x in (out/'history.jsonl').read_text().splitlines()]
 assert len(history)==100 and [h['event'] for h in history if h['role']=='user']==spec['events']
