import json
import run_probe3 as p
from run_benchmark import save,load

def test_probe_detects_caller_mutation(tmp_path,monkeypatch):
 original=p.ROOT
 class Roots:
  def __truediv__(self,sub):return tmp_path/sub if sub=='iteration3-runs' else original/sub
 monkeypatch.setattr(p,'ROOT',Roots());monkeypatch.setattr(p,'WORKSPACE',tmp_path)
 def fake(model,cwd,prompt,out):
  h=[json.loads(x) for x in (cwd/'history.jsonl').read_text().splitlines()];t=h[-1]['event']['turn']
  if t==3:(cwd/'ledger.jsonl').write_text('unsolicited edit')
  out.mkdir(parents=True);s={'usage':{'input_tokens':1,'output_tokens':1},'local_process_metrics':{}};save(out/'status.json',s);return f'ACK P{t:02d}',s
 monkeypatch.setattr(p,'native',fake);p.run('astra','on')
 c=load(tmp_path/'outputs/helix-frontier/iteration3/astra/probe/on/checks.json')
 assert len(c)==5 and c[2]['caller_files_unchanged'] is False
 assert all(x['exact_ack'] for x in c)
