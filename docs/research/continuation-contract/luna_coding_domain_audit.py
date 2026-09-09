"""Post-hoc finite domain audit; not a new model run or unseen benchmark."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import time


def expected(total, weights):
    if total == 0: return [0] * len(weights)
    quotas=[Fraction(total) * w / sum(weights) for w in weights]
    floors=[q.numerator // q.denominator for q in quotas]
    ranked=sorted(range(len(weights)), key=lambda i: (-(quotas[i]-floors[i]), i))
    for i in ranked[:total-sum(floors)]: floors[i]+=1
    return floors


def audit(root):
    root=Path(root);rng=random.Random(910271);cases=[]
    for _ in range(1200):
        n=rng.randrange(1,33)
        bits=rng.choice((8,64,256,1024,2048))
        total=rng.getrandbits(bits)
        weights=[rng.getrandbits(rng.choice((1,8,64,256))) for _ in range(n)]
        if not sum(weights):weights[0]=1
        cases.append((total,weights,expected(total,weights)))
    rows=[]
    for arm in ('off','on'):
        files={n:(root/arm/n).read_bytes() for n in ('allocation.py','settings.json','test_allocation.py')}
        spec=importlib.util.spec_from_file_location('qualified_'+arm,root/arm/'allocation.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        f=mod.allocate;started=time.perf_counter();valid=invalid=0
        for total,weights,wanted in cases:
            original=weights.copy();got=f(total,weights)
            assert got==wanted and all(type(x) is int for x in got) and sum(got)==total
            assert weights==original;valid+=1
        for total,weights in [(0,[]),(0,[0,0]),(7,[1]*20),(10**100,[1,1,1])]:
            for form in (list,tuple,iter):
                assert f(total,form(weights))==expected(total,weights);valid+=1
        class Int(int):pass
        assert f(Int(5),[Int(1),Int(1),Int(1)])==[2,2,1];valid+=1
        bad=[(v,[1]) for v in (True,False,-1,1.0,None,'2')]
        bad += [(1,[v]) for v in (True,False,-1,1.0,None,'2')]
        bad += [(1,[]),(1,[0,0]),(0,[True]),(0,[1.0]),(0,None),(1,object())]
        for total,weights in bad:
            try:f(total,weights)
            except ValueError:invalid+=1
            else:raise AssertionError((arm,total,weights))
        for name,raw in files.items():assert (root/arm/name).read_bytes()==raw
        rows.append({'arm':arm,'checks':'PASS','large_integer_and_container_cases':valid,'invalid_cases':invalid,
                     'source_sha256':hashlib.sha256(files['allocation.py']).hexdigest(),
                     'evaluation_seconds':time.perf_counter()-started})
    result={'classification':'Post-hoc independent rational-arithmetic and Python edge-case audit; not holdout or model inference',
            'seed':910271,'rows':rows,'new_model_calls':0,'auditor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limits':['Finite ordinary-int/container domain; arbitrary overloaded Python objects and resource exhaustion unproved',
                      'Generated cases after seeing source shape; not prospective model qualification',
                      'No native output or prompt changed']}
    (root/'domain-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    Path(__file__).with_name('LUNA_CODING_DOMAIN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':audit(sys.argv[1])
