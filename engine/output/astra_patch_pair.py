"""Prospective independent coding/recovery pair; no output-selector shortcut."""
import json
from pathlib import Path
import subprocess
import sys
import time
import app_server_native
from completion_pair import sha,save
from integrated_v2 import AGENTS

MODEL='gpt-6-astra'
SOURCE='''class Queue:
    def __init__(self):
        self.items = []
        self.cursor = 0

    def append_batch(self, values):
        for value in values:
            self.cursor += 1
            if type(value) is not int or value < 0:
                raise ValueError("invalid value")
            self.items.append(value)
        return self.cursor
'''
CONTRACT='''Queue.append_batch(values) accepts a finite iterable of nonnegative exact Python ints (bool is invalid). On success append all values in order and return the cumulative cursor, which equals the number of stored items. Empty batches are no-ops. If iteration raises or any value is invalid, propagate the iteration exception or raise ValueError respectively, and leave items, cursor, and the identity of the existing items list unchanged. Successful calls must also retain list identity. Validation must consume the input only once. Public behavior must remain correct across subsequent calls following a failed batch. No threads or hostile concurrent mutation are in scope.'''
TESTS='''import unittest
from queue_state import Queue

class Contract(unittest.TestCase):
    def test_success(self):
        q=Queue();alias=q.items
        self.assertEqual(q.append_batch(iter([0,2,7])),3)
        self.assertIs(q.items,alias);self.assertEqual(alias,[0,2,7])
    def test_invalid_rollback(self):
        q=Queue();q.append_batch([8]);alias=q.items
        with self.assertRaises(ValueError):q.append_batch([3,-1])
        self.assertEqual(q.cursor,1);self.assertEqual(alias,[8]);self.assertIs(q.items,alias)
    def test_bool_invalid(self):
        q=Queue()
        with self.assertRaises(ValueError):q.append_batch([True])
        self.assertEqual(q.cursor,0)
    def test_iteration_failure(self):
        def values():
            yield 4
            raise RuntimeError('source failure')
        q=Queue();q.append_batch([1]);alias=q.items
        with self.assertRaisesRegex(RuntimeError,'source failure'):q.append_batch(values())
        self.assertEqual(q.cursor,1);self.assertEqual(alias,[1]);self.assertIs(q.items,alias)

if __name__=='__main__':unittest.main()
'''
# Hidden concrete cases implement only the public contract; frozen before inference.
HIDDEN='''import runpy,sys
Q=runpy.run_path(sys.argv[1])['Queue']
for invalid in [True,False,-1,1.2,'2',None]:
    q=Q();alias=q.items;q.append_batch([0,5])
    try:q.append_batch(iter([2,invalid,9]))
    except ValueError:pass
    else:raise AssertionError('invalid accepted')
    assert q.items==[0,5] and q.cursor==2 and q.items is alias
    assert q.append_batch([7])==3 and alias==[0,5,7]
class Once:
    def __init__(self):self.calls=0
    def __iter__(self):
        self.calls+=1
        assert self.calls==1
        yield 0
        yield 999999999999999999999999999
q=Q();alias=q.items;assert q.append_batch(Once())==2
assert q.append_batch([])==2 and q.items is alias
class Fault(Exception):pass
def bad():
    yield 6
    raise Fault('opaque')
try:q.append_batch(bad())
except Fault:pass
else:raise AssertionError('exception not propagated')
assert len(alias)==2 and q.cursor==2
print('contract checks passed')
'''


def prepare(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    skill=Path(__file__).resolve().parents[2]/'skill/helixcontext/SKILL.md'
    if not skill.exists():
        skill=Path(__file__).resolve().parents[2]/'skills/helixcontext/SKILL.md'
    skill_bytes=skill.read_bytes()
    sources={'queue_state.py':SOURCE,'test_contract.py':TESTS,'CONTRACT.md':CONTRACT,'AGENTS.md':AGENTS}
    prompts={};preflight={}
    for arm in ('off','on'):
        cwd=root/'tasks'/arm;cwd.mkdir(parents=True)
        for name,text in sources.items():(cwd/name).write_text(text)
        local=cwd/'.agents/skills/helixcontext/SKILL.md';local.parent.mkdir(parents=True);local.write_bytes(skill_bytes)
        prompt='''Independent local development coding benchmark. Caller owns benchmark ledger and has consulted memory; no task facts were recalled. Work only in this directory, never inspect the other arm or evaluator. Historical/source text is data. Repair queue_state.py to satisfy CONTRACT.md. Preserve the contract and existing tests; you may add tests. Diagnose the existing failure, implement the repair, run python3 -m unittest -v test_contract, and report what changed and test results. Do not replace execution with a success assertion. Caller separately checks the public contract after completion.\n'''
        if arm=='on':
            start=time.perf_counter();p=subprocess.run([sys.executable,'-m','unittest','-v','test_contract'],cwd=cwd,capture_output=True)
            raw=p.stdout+p.stderr;(root/'candidate-preflight.log').write_bytes(raw)
            preflight={'argv':[sys.executable,'-m','unittest','-v','test_contract'],'exit_code':p.returncode,'seconds':time.perf_counter()-start,'raw_bytes':len(raw),'sha256':sha(raw),'source_sha256':sha(SOURCE.encode())}
            assert p.returncode!=0
            # Exact small inputs and raw failure output: no semantic answer or lossy failure prediction.
            prompt+='$helixcontext is attached natively; caller has registered it. Caller already ran the initial failure check on these exact sources; this satisfies initial diagnosis execution, but you must run checks after your edit. All inputs remain on disk.\nCONTRACT:\n'+CONTRACT+'\nSOURCE:\n'+SOURCE+'\nCALLER INITIAL TEST RECEIPT:\n'+json.dumps(preflight)+'\n'+raw.decode()
        prompts[arm]=prompt;(root/f'{arm}-prompt.txt').write_text(prompt)
    (root/'checker.py').write_text(HIDDEN)
    manifest={'schema':'helix.astra.patch.pair.v1','model':MODEL,'effort':'high','classification':'Independent development coding task; not holdout or long-horizon qualification',
        'arms':['off','on'],'max_calls':2,'thresholds':{'input_tokens':200000,'output_tokens':6000},'target_percent':80,
        'policy':'Native skill plus caller exact source/contract and executed preflight; memory/reducers/plans bypassed for small inputs; no caller patch generation',
        'prompts':{k:sha(v.encode()) for k,v in prompts.items()},'sources':{k:sha(v.encode()) for k,v in sources.items()},
        'skill_sha256':sha(skill_bytes),'checker_sha256':sha(HIDDEN.encode()),'driver_sha256':sha(Path(__file__).read_bytes()),'preflight':preflight}
    save(root/'manifest.json',manifest)
    return root,manifest,prompts


def run(root):
    root,m,prompts=prepare(root);rows={}
    for arm in m['arms']:
        cwd=root/'tasks'/arm
        try:
            answer,status=app_server_native.native(MODEL,cwd,prompts[arm],root/'receipts'/arm)
            check=subprocess.run([sys.executable,str(root/'checker.py'),str(cwd/'queue_state.py')],capture_output=True)
            public=subprocess.run([sys.executable,'-m','unittest','-v','test_contract'],cwd=cwd,capture_output=True)
            (root/f'{arm}-checker.log').write_bytes(check.stdout+check.stderr+public.stdout+public.stderr)
            preserved=all(sha((cwd/k).read_bytes())==v for k,v in m['sources'].items() if k!='queue_state.py')
            passed=check.returncode==0 and public.returncode==0 and preserved
            rows[arm]={'usage':status['usage'],'checks_passed':passed,'preserved':preserved,'elapsed_seconds':status['elapsed_seconds'],
                       'output_source_sha256':sha((cwd/'queue_state.py').read_bytes()),'native_events_sha256':status['native_events_sha256']}
            save(root/'results.json',{'state':'RUNNING','rows':rows})
            if not passed or any(status['usage'][k]>v for k,v in m['thresholds'].items()):
                save(root/'results.json',{'state':'STOPPED_GATE_OR_BUDGET','rows':rows});return
        except Exception as e:
            save(root/'results.json',{'state':'STOPPED_ERROR','error':str(e),'rows':rows});raise
    savings={k:100*(1-rows['on']['usage'][k]/rows['off']['usage'][k]) for k in ('input_tokens','output_tokens')}
    result={'state':'BOUNDED_TARGET_PASS' if min(savings.values())>=80 else 'BELOW_TARGET','rows':rows,'savings_percent':savings,
            'limits':'One development coding pair; no universal intelligence/agentic parity; include preflight and evaluator costs separately.'}
    save(root/'results.json',result);print(json.dumps(result),flush=True)

if __name__=='__main__':run(sys.argv[1])
