"""One prospective Astra High transfer pair; Sol source/policy stay frozen."""
import json
from pathlib import Path
import sys
import integrated_pair as base
import integrated_v3
import app_server_native
from completion_pair import sha,save

MODEL='gpt-6-astra'


def prepare(root):
    root,m,prompts,runtimes,catalog,expected=integrated_v3.prepare(root)
    assert m['model']==MODEL
    m.update(schema='helix.astra_transfer.v1',classification='Fresh Astra High app-server development transfer; one reused task family, no general parity',
        post_call_thresholds={'input_tokens':200000,'output_tokens':6000},
        transfer={'reason':'Prior Astra renderer inspected helpers; move mechanics to caller and use native skill attachment.',
                  'target':'At least 80 percent separately on native input and output, with exact checks.',
                  'max_calls':2,'candidate_selection':'Fixed before either arm; no native tuning or historical control reuse.',
                  'budget_reason':'Raised prospectively for both app-server arms after observed Sol control 167119 input; not amended after this result.'})
    m['dependencies'][str(Path(__file__).resolve())]=sha(Path(__file__).read_bytes())
    save(root/'manifest.json',m)
    return root,m,prompts,runtimes,catalog,expected


def run(root):
    base.MODEL=MODEL;base.prepare=prepare;base.native=app_server_native.native;base.run(root)
    path=Path(root)/'results.json';result=json.loads(path.read_text())
    if result['state'].startswith('SOL_V1_'):
        result['state']='ASTRA_V1_80_80_CANDIDATE' if min(result['savings_percent'].values())>=80 else 'ASTRA_BELOW_80_TARGET'
    result['model']=MODEL;result['transfer_only']=True
    save(path,result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)


if __name__=='__main__':run(sys.argv[1])
