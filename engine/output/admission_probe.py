"""Exercise real pinned research profile; no native model call or task execution."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'prototype'))
from admission import Request,decide


def probe():
    repo=Path(__file__).resolve().parents[2]
    q=json.loads((repo/'engine/profiles/sol-high-v1-research-admission.json').read_text())
    cases={}
    for model in ('gpt-5.6-sol','gpt-6-astra','gpt-5.6-luna'):
        for mode in ('production','qualified_fixture_research'):
            r=Request(model,'high',q['contract_hash'],mode)
            cases[model+'/'+mode]=decide(r,qualification=q,repo=repo)
    assert cases['gpt-5.6-sol/qualified_fixture_research']['route']=='optimized'
    assert all(v['route']=='native' for k,v in cases.items() if k!='gpt-5.6-sol/qualified_fixture_research')
    return {'classification':'Admission engineering probe only; no native execution, savings or parity measurement',
            'decisions':cases,'caller_obligation':'Request contract hash must describe the verified actual task, not a label supplied by model output.',
            'remaining_limits':['No global platform hook installed','Gate validates before callback; concurrent file mutation during execution is not prevented',
                                'Qualified research input remains caller-owned and trusted','Production no-loss and net-economics qualification absent']}

if __name__=='__main__':print(json.dumps(probe(),indent=2))
