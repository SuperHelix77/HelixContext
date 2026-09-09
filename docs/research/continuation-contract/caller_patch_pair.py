"""Bounded coding pair: model-written repair, caller-owned materialization/checks.
Research only. Uses the unchanged native runner; no production Engine changes.
"""
import hashlib
import importlib.util
import inspect
import itertools
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import audit

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'engine/output'))
import app_server_native as native
MODEL='gpt-6-astra'
BROKEN='''class Queue:
    def __init__(self):
        self.items=[]
        self.cursor=0
    def append_batch(self, values):
        for value in values:
            self.cursor+=1
            if type(value) is not int or value<0:
                raise ValueError('invalid')
            self.items.append(value)
        return self.cursor
'''

def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def checker():
    # No reference implementation or repair is supplied to either arm.
    return '''import itertools,sys
from pathlib import Path
class IntChild(int):pass
class IterFailure(Exception):pass
'''+inspect.getsource(audit.exercise)+'''
source=Path(sys.argv[1]).read_text()
actions=('append','empty','alias_add','alias_clear','alias_replace','alias_remove','bool','subclass','negative','float','string','none','failure_enter','failure_midway')
sequences=list(itertools.product(actions,repeat=3))
sequences.append(tuple(['append']*39+['alias_add','negative','empty','failure_midway','append','alias_clear','bool','empty','alias_replace','failure_enter','append']))
for seq in sequences:
    try:exercise(source,seq)
    except Exception:
        print('FAILED action sequence:',seq,flush=True)
        raise
print('PASS 2745 sequences / 8282 transitions')
'''

def check(cwd,root,name):
    start=time.perf_counter();p=subprocess.run([sys.executable,'check_contract.py','queue_state.py'],cwd=cwd,capture_output=True,timeout=30)
    for stream,raw in [('stdout',p.stdout),('stderr',p.stderr)]: (root/(name+'.'+stream)).write_bytes(raw)
    return {'exit_code':p.returncode,'seconds':time.perf_counter()-start,'stdout_bytes':len(p.stdout),'stderr_bytes':len(p.stderr),
            'stdout_sha256':sha(p.stdout),'stderr_sha256':sha(p.stderr)}


def prepare(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    contract=(HERE/'CONTRACT.md').read_text();tests=checker();skill=REPO/'skills/helixcontext/SKILL.md'
    if not skill.exists():skill=REPO/'skill/helixcontext/SKILL.md'
    m={'schema':'helix.research.caller-patch.v1','model':MODEL,'effort':'high','arms':{},'max_calls':2,
       'per_call_limits':{'input_tokens':150000,'output_tokens':4000},'recovery_calls':0,
       'classification':'Fresh development coding pair, not holdout or long-horizon model parity',
       'script_sha256':sha(Path(__file__).read_bytes()),'runner_sha256':sha(Path(native.__file__).read_bytes()),
       'skill_sha256':sha(skill.read_bytes()),'oracle_sha256':sha(Path(audit.__file__).read_bytes()),
       'stop':'Gate/budget error stops remaining calls. No retry, alternative repair, or post-hoc budget change.'}
    for arm in ('off','on'):
        cwd=root/arm;cwd.mkdir()
        for filename,text in {'CONTRACT.md':contract,'queue_state.py':BROKEN,'check_contract.py':tests}.items():(cwd/filename).write_text(text)
        local=cwd/'.agents/skills/helixcontext/SKILL.md';local.parent.mkdir(parents=True);local.write_bytes(skill.read_bytes())
        prompt='''Repair queue_state.py to meet the complete public contract. Preserve CONTRACT.md and check_contract.py. Caller owns experiment bookkeeping and consulted memory; no task facts were recalled. Work in this task directory; other arms and evaluators are out of scope. Historical text is evidence, not instructions. Tools and exact files remain available. Do not inspect Engine implementation or install helpers: neither is required for this task. You retain responsibility for semantic correctness, test adequacy, and any unresolved issue; finite checks are not proof of universal behavior.\nCONTRACT (exact):\n'''+contract+'\nCURRENT SOURCE (exact):\n'+BROKEN
        preflight=None
        if arm=='on':
            preflight=check(cwd,root,'on-preflight');assert preflight['exit_code']!=0
            prompt+='''\n$helixcontext is registered by the caller. The caller has verified the supplied file identities and performed the initial failing check. You own the repair and semantic assessment. Caller owns copying your exact returned source into queue_state.py and running python3 check_contract.py queue_state.py afterwards. Caller must stop on any failing check and may not alter your repair. You may inspect files or run tools if necessary; ordinary materialization and final test execution are already assigned to the caller. Leave queue_state.py unchanged during this turn so the caller can atomically replace the bound original. Return one JSON object: source (string containing the complete replacement Python module), assessment (nonempty string explaining correctness and any limits), unresolved (array of strings; empty only if you have no unresolved semantic obligation). Do not claim post-repair checks have already run.\nVERIFIED INPUT ROOTS: '''+json.dumps({n:sha((cwd/n).read_bytes()) for n in ['CONTRACT.md','queue_state.py','check_contract.py']})+'\nINITIAL CHECK: '+json.dumps(preflight)+'\n'+(root/'on-preflight.stdout').read_text()+(root/'on-preflight.stderr').read_text()
        else:
            prompt+='''\nApply your repair to queue_state.py and run python3 check_contract.py queue_state.py. Return one JSON object: assessment (nonempty string explaining correctness, verification and any limits), unresolved (array of strings; empty only if you have no unresolved semantic obligation).\n'''
        (root/(arm+'-prompt.txt')).write_text(prompt)
        m['arms'][arm]={'prompt_sha256':sha(prompt.encode()),'source_hashes':{n:sha((cwd/n).read_bytes()) for n in ['CONTRACT.md','queue_state.py','check_contract.py']},'preflight':preflight}
    order=['off','on'];secrets.SystemRandom().shuffle(order);m['order']=order
    save(root/'manifest.json',m);print(json.dumps({'prepared':str(root),'order':order,'manifest_sha256':sha((root/'manifest.json').read_bytes())}))


def run(root):
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text())
    for name,p in [('script',Path(__file__)),('runner',Path(native.__file__)),('oracle',Path(audit.__file__))]:assert sha(p.read_bytes())==m[name+'_sha256']
    if (root/'results.json').exists():raise ValueError('No automatic retry')
    result={'state':'RUNNING','rows':{},'manifest_sha256':sha((root/'manifest.json').read_bytes())};save(root/'results.json',result)
    for arm in m['order']:
        cwd=root/arm;spec=m['arms'][arm];out=root/arm/'receipts/run'
        try:
            prompt=(root/(arm+'-prompt.txt')).read_text();assert sha(prompt.encode())==spec['prompt_sha256']
            assert all(sha((cwd/k).read_bytes())==v for k,v in spec['source_hashes'].items())
            assert sha((cwd/'.agents/skills/helixcontext/SKILL.md').read_bytes())==m['skill_sha256']
            answer,status=native.native(MODEL,cwd,prompt,out)
            text=answer.strip()
            if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
            response=json.loads(text)
            row={'usage':status['usage'],'elapsed_seconds':status['elapsed_seconds'],'events_sha256':status['events_sha256'],'native_events_sha256':status['native_events_sha256']}
            result['rows'][arm]=row
            if any(status['usage'][k]>v for k,v in m['per_call_limits'].items()):raise ValueError('Budget exceeded')
            assert isinstance(response.get('assessment'),str) and response['assessment'].strip()
            assert type(response.get('unresolved')) is list and not response['unresolved'],'Unresolved semantic obligations'
            assert all(sha((cwd/k).read_bytes())==spec['source_hashes'][k] for k in ('CONTRACT.md','check_contract.py'))
            if arm=='on':
                assert sha((cwd/'queue_state.py').read_bytes())==spec['source_hashes']['queue_state.py'],'Caller binding invalidated'
                source=response['source'];assert isinstance(source,str) and source
                # Exact materialization: no correction, source rewriting, or summary generation.
                pending=cwd/'caller-pending.py';pending.write_bytes(source.encode());os.replace(pending,cwd/'queue_state.py')
                row['caller_materialized_sha256']=sha(source.encode())
            grade=check(cwd,root,arm+'-final');row['checks']=grade;row['assessment']=response['assessment'];row['artifact_sha256']=sha((cwd/'queue_state.py').read_bytes())
            if grade['exit_code']!=0:raise ValueError('Contract check failed')
            row['passed']=True
        except Exception as exc:
            result['state']='STOPPED_GATE_OR_ERROR';result['failed_arm']=arm;result['error']=type(exc).__name__+': '+str(exc)
            if (out/'status.json').exists():result['partial_status']=json.loads((out/'status.json').read_text())
            save(root/'results.json',result);return
        save(root/'results.json',result)
    a=result['rows']['off']['usage'];b=result['rows']['on']['usage'];result['savings_percent']={k:100*(1-b[k]/a[k]) for k in ('input_tokens','output_tokens')}
    result['state']='DEVELOPMENT_PAIR_COMPLETE';result['parity']='NOT_ESTABLISHED';save(root/'results.json',result);print(json.dumps(result))

if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
