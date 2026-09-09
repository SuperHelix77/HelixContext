"""Offline research fixture audit only. No Engine integration or model invocation.

All candidate code is supplied as task data to BOTH future paired arms.
This audit tests checker discrimination, not model capability or savings.
"""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

CONTRACT = '''append_batch(values) consumes one finite iterable once. Accept only nonnegative
exact Python ints (bool and int subclasses are invalid). Append in order to the
existing items list, preserve its identity, and return the cumulative item count.
An invalid value raises ValueError. An iteration exception propagates unchanged.
Either failure leaves items, list identity, and cursor unchanged. Subsequent calls
must still work. No concurrency is in scope.
'''
GOOD = '''class Queue:
    def __init__(self):
        self.items = []
        self.cursor = 0
    def append_batch(self, values):
        pending = []
        for value in values:
            if type(value) is not int or value < 0:
                raise ValueError('invalid value')
            pending.append(value)
        self.items.extend(pending)
        self.cursor += len(pending)
        return self.cursor
'''
BAD = GOOD.replace('type(value) is not int', 'not isinstance(value, int)')
MECHANICAL = '''import runpy,sys
Q = runpy.run_path(sys.argv[1])['Queue']
q=Q(); alias=q.items
assert q.append_batch(iter([0,2,7]))==3
assert q.items is alias and alias==[0,2,7]
assert q.append_batch([])==3
try: q.append_batch([4,-1])
except ValueError: pass
else: raise AssertionError('negative value accepted')
assert q.items is alias and alias==[0,2,7] and q.cursor==3
print('ordinary-int order, empty batch, negative rollback: PASS')
'''
SEMANTIC = '''import runpy,sys
Q=runpy.run_path(sys.argv[1])['Queue']
class IntSubclass(int): pass
for invalid in [True,False,IntSubclass(2),-1,1.5,'2',None]:
    q=Q(); alias=q.items; q.append_batch([8])
    try: q.append_batch(iter([3,invalid,4]))
    except ValueError: pass
    else: raise AssertionError('invalid accepted: '+repr(invalid))
    assert q.items is alias and alias==[8] and q.cursor==1
    assert q.append_batch([7])==2 and alias==[8,7]
class Fault(Exception): pass
fault=Fault('iteration failure')
def broken():
    yield 9
    raise fault
q=Q();alias=q.items;q.append_batch([1])
try: q.append_batch(broken())
except Fault as exc: assert exc is fault
else: raise AssertionError('iteration exception lost')
assert q.items is alias and alias==[1] and q.cursor==1
class Once:
    def __init__(self): self.calls=0
    def __iter__(self):
        self.calls+=1
        assert self.calls==1
        yield 0
        yield 10**100
assert q.append_batch(Once())==3 and q.items is alias
assert alias==[1,0,10**100] and q.cursor==3
assert q.append_batch([])==3
print('finite semantic contract cases: PASS')
'''


def sha(raw): return hashlib.sha256(raw).hexdigest()
def write_json(path,data): path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')


def audit(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    files={'CONTRACT.md':CONTRACT,'proposed_valid.py':GOOD,'proposed_wrong.py':BAD,
           'mechanical_checker.py':MECHANICAL,'semantic_checker.py':SEMANTIC}
    for name,data in files.items(): (root/name).write_text(data)
    results={}
    for proposal in ('valid','wrong'):
        results[proposal]={}
        for checker in ('mechanical','semantic'):
            argv=[sys.executable,str(root/(checker+'_checker.py')),str(root/('proposed_'+proposal+'.py'))]
            t=time.perf_counter();p=subprocess.run(argv,capture_output=True,timeout=10)
            # Keep stdout and stderr separately, exactly. No model execution.
            logs={}
            for stream,raw in [('stdout',p.stdout),('stderr',p.stderr)]:
                name=f'{proposal}-{checker}.{stream}';(root/name).write_bytes(raw)
                logs[stream]={'path':name,'sha256':sha(raw),'bytes':len(raw)}
            results[proposal][checker]={'argv':argv,'exit_code':p.returncode,'seconds':time.perf_counter()-t,'logs':logs}
    mutations={
        'reverse_order':GOOD.replace('extend(pending)','extend(reversed(pending))'),
        'replace_list':GOOD.replace('self.items.extend(pending)','self.items = self.items + pending'),
        'double_consumption':GOOD.replace('pending = []','list(values)\n        pending = []'),
        'cursor_corruption':GOOD.replace('self.cursor += len(pending)','self.cursor += 1')}
    mutation_results={}
    for name,code in mutations.items():
        target=root/('mutation-'+name+'.py');target.write_text(code)
        t=time.perf_counter()
        p=subprocess.run([sys.executable,str(root/'semantic_checker.py'),str(target)],capture_output=True,timeout=10)
        (root/(name+'.stdout')).write_bytes(p.stdout);(root/(name+'.stderr')).write_bytes(p.stderr)
        mutation_results[name]={'exit_code':p.returncode,'seconds':time.perf_counter()-t}
    roots={name:sha((root/name).read_bytes()) for name in files}
    # Research receipt examples, not a new production schema or verifier.
    for proposal in ('valid','wrong'):
        receipt={'research_only':True,'operation':'review-supplied-proposal','version':1,
            'contract_root':roots['CONTRACT.md'],'proposal_root':roots['proposed_'+proposal+'.py'],
            'checker_root':roots['mechanical_checker.py'],'execution':results[proposal]['mechanical'],
            'checked':['ordinary-int order','empty batch','negative rollback'],
            'unchecked':['exact-int eligibility including bool/subclasses','iteration-failure atomicity',
                         'single consumption','overall semantic adequacy'],
            'status':'PASS' if results[proposal]['mechanical']['exit_code']==0 else 'FAIL'}
        write_json(root/(proposal+'-receipt.json'),receipt)
    stale=json.loads((root/'valid-receipt.json').read_text())
    old_contract=CONTRACT.replace('exact Python ints (bool and int subclasses are invalid)',
                                  'Python ints including bool and int subclasses')
    (root/'old-CONTRACT.md').write_text(old_contract)
    stale['contract_root']=sha(old_contract.encode());write_json(root/'stale-receipt.json',stale)
    # Demonstrate the mismatch, without applying anything or treating hashes as semantic proof.
    before=sha((root/'proposed_valid.py').read_bytes())
    mismatch=stale['contract_root']!=roots['CONTRACT.md']
    assertions={
        'all_four_contract_mutations_rejected':all(r['exit_code']!=0 for r in mutation_results.values()),
        'valid_mechanical_pass':results['valid']['mechanical']['exit_code']==0,
        'valid_semantic_pass':results['valid']['semantic']['exit_code']==0,
        'wrong_mechanical_pass':results['wrong']['mechanical']['exit_code']==0,
        'wrong_semantic_fail':results['wrong']['semantic']['exit_code']!=0,
        'stale_contract_mismatch':mismatch,
        'no_apply_on_stale':before==sha((root/'proposed_valid.py').read_bytes()),
        'wrong_receipt_binds_real_wrong_source':json.loads((root/'wrong-receipt.json').read_text())['proposal_root']==sha(BAD.encode()),
    }
    manifest={'schema':'helix.research.fixture-audit.v1','classification':'ZERO_CALL_CHECKER_DISCRIMINATION_ONLY',
        'native_calls':0,'engine_changes':0,'model_parity':'UNTESTED','token_savings':'UNMEASURED',
        'assertions':assertions,'mutation_results':mutation_results,'executions':results,'python':platform.python_version(),
        'script_sha256':sha(Path(__file__).read_bytes()),'source_roots':roots,
        'seconds':time.perf_counter()-start,'physical_io_bytes':None,
        'limitations':['no production transactionality or TOCTOU claim','no model exposed to fixtures',
                      'finite semantic checks, not proof of all valid Python behavior',
                      'development fixture derived from public prior failure family, not holdout'],
        'files':{p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(root.iterdir()) if p.is_file()}}
    write_json(root/'audit.json',manifest)
    assert all(assertions.values()),assertions
    print(json.dumps({'root':str(root),'assertions':assertions,'native_calls':0,'seconds':manifest['seconds']}))

if __name__=='__main__': audit(sys.argv[1])
