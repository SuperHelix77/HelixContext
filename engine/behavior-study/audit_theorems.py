"""Finite audits of the stated algebra; proofs and assumptions are in THEOREMS.md."""
import itertools,json
from pathlib import Path
checks=0
for weights in itertools.product(range(3),repeat=3):
 for a in range(8):
  for b in range(8):
   for overhead in (0,1,5):
    baseline=sum(weights)
    surviving=sum(w for i,w in enumerate(weights) if not ((a|b)>>i)&1)
    removed=sum(w for i,w in enumerate(weights) if ((a|b)>>i)&1)
    assert baseline-(surviving+overhead)==removed-overhead
    checks+=1
for n in range(1,7):
 for statuses in itertools.product((0,1,7),repeat=n):
  observed=[]
  for s in statuses:
   observed.append(s)
   if s:break
  success=len(observed)==n and all(s==0 for s in observed)
  assert success==all(s==0 for s in statuses)
  checks+=1
assert (1,0)[-1]==(0,0)[-1]
result={'finite_checks':checks,'passed':True,'scope':'Finite algebra and control-flow audits; no model evidence or proof beyond stated premises','new_model_calls':0}
Path(__file__).with_name('theorem-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
