"""Three development capability pairs; no retries, full ordinary tool access.

Tests the V7 base/skill product surface outside its narrow W50 renderer.
Cold retrieval is a snapshot test, not a replay of 40 native turns.
"""
import base64
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import native_kernel_pair as kd

COMMON = ('Caller completed memory consultation; no relevant facts were recalled. '
          'Caller owns benchmark bookkeeping. Work only in this task directory; '
          'other runs and evaluators are out of scope. Ordinary tools and semantic '
          'review remain available. Complete the requested task and report actual results.\n')


def prepare(root, v7):
    root, v7 = Path(root).resolve(), Path(v7)
    root.mkdir(parents=True, exist_ok=False)
    protocol = kd.REPO/'benchmarks/frozen-high/protocol'
    specs = {k: json.loads((protocol/n).read_text()) for k,n in {
        'coding':'agentic-v1.json', 'selection':'reasoning-v2.json',
        'cold':'latent-v1/delay-40.json'}.items()}
    kernel = root/'luna-base-v1.md'; kernel.write_bytes((v7/'luna-base-v1.md').read_bytes())
    bound = [Path(__file__), kernel, Path('/Users/mert/.codex/AGENTS.md'),
             Path(kd.__file__), kd.REPO/'engine/output/research_session.py',
             kd.REPO/'engine/output/app_server_native.py']
    for case, spec in specs.items():
        kd.save(root/(case+'-source.json'), spec); bound.append(root/(case+'-source.json'))
        for arm in ('default','helix'):
            cwd=root/case/arm; cwd.mkdir(parents=True)
            skill=cwd/'.agents/skills/helixcontext/SKILL.md'; skill.parent.mkdir(parents=True)
            skill.write_bytes((kd.REPO/'skills/helixcontext/SKILL.md').read_bytes()); bound.append(skill)
            if case=='coding':
                for name, text in spec['files'].items(): (cwd/name).write_text(text)
                prompt=COMMON+spec['task']
                bound += [cwd/'settings.json',cwd/'test_allocation.py']
            elif case=='selection':
                kd.save(cwd/'records.json',spec['records']);bound.append(cwd/'records.json')
                prompt=COMMON+spec['task']
            else:
                kd.save(cwd/'history.json',spec['events'][:-1]);bound.append(cwd/'history.json')
                prompt=COMMON+spec['events'][-1]['request']+'\nComplete exact prior events are in history.json. Read whatever evidence you need. This is a cold-history recovery task; no importance ranking or answer has been supplied.'
            (cwd/'prompt.txt').write_text(prompt);bound.append(cwd/'prompt.txt')
    kd.save(root/'manifest.json',{'model':'gpt-5.6-luna','effort':'high','kernel':str(kernel),
        'order':[['coding','helix'],['coding','default'],['selection','default'],['selection','helix'],['cold','helix'],['cold','default']],
        'retries':0,'sha256':{str(p):kd.sha(p) for p in bound},
        'classification':'Three known development tasks, product base/skill comparison, not isolated Engine ablation or holdout',
        'route':'Ordinary native tools on these unsupported W50-renderer cells; no forced semantic serialization',
        'stop':'Stop on runtime, integrity or behavioral failure; preserve costs. No model retry.',
        'limits':['Cold snapshot task is not a 40-turn continuation/compaction test.',
                  'Prior fixture exposure and nonrandom counterbalanced order; no population parity inference.']})
    print(kd.sha(root/'manifest.json'))


def verify(m):
    for p,h in m['sha256'].items(): assert kd.sha(Path(p))==h,p


def parse(answer):
    text=answer.strip()
    if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
    return json.loads(text)


def grade(root,case,cwd,answer):
    spec=json.loads((root/(case+'-source.json')).read_text())
    if case=='selection':
        eligible=[{'id':r['id'],'amount_exact':r['amount_exact'],'duration_ms':r['duration_ms']}
                  for r in spec['records'] if r['status']=='ready' and r['consent'] is True and r['approvals']>=2]
        expected={'total_count':len(spec['records']),'eligible':sorted(eligible,key=lambda r:r['id']),
                  'job_0177_eligible':any(r['id']=='job-0177' for r in eligible)}
        assert json.dumps(parse(answer),sort_keys=True)==json.dumps(expected,sort_keys=True)
        return {'exact_selection':'PASS'}
    if case=='cold':
        request=spec['events'][-1]['request'];tag=request.split('inventory tag ')[1].split('.')[0]
        matches=[(e,n) for e in spec['events'][:-1] for n in e.get('data',{}).get('notes',[]) if n.get('inventory_tag')==tag]
        assert len(matches)==1
        e,n=matches[0]; expected={'inventory_tag':tag,'label_exact':n['label_exact'],
            'label_utf8_base64':base64.b64encode(n['label_exact'].encode()).decode(),
            'sequence_exact':n['sequence_exact'],'evidence_turn':e['turn']}
        assert json.dumps(parse(answer),sort_keys=True,ensure_ascii=False)==json.dumps(expected,sort_keys=True,ensure_ascii=False)
        return {'exact_late_detail':'PASS'}
    # Independent mathematical oracle in private staging; do not change model files.
    script='''import allocation as a, itertools, inspect, unittest
assert list(inspect.signature(a.allocate).parameters)==['total','weights']
suite=unittest.defaultTestLoader.discover('.',pattern='test_allocation.py')
assert unittest.TextTestRunner().run(suite).wasSuccessful()
count=0
for n in range(5):
 for w in itertools.product(range(4),repeat=n):
  for total in range(13):
   if total and not sum(w):
    try:a.allocate(total,list(w))
    except ValueError:pass
    else:raise AssertionError((total,w))
   else:
    if not total: expected=[0]*n
    else:
     den=sum(w);expected=[total*x//den for x in w]
     order=sorted(range(n),key=lambda i:(-(total*w[i]%den),i))
     for i in order[:total-sum(expected)]:expected[i]+=1
    got=a.allocate(total,list(w));assert got==expected and all(type(x)is int for x in got),(total,w,got,expected)
   count+=1
for t,w in [(True,[1]),(-1,[1]),(1.5,[1]),(2,[True]),(2,[-1]),(2,[1.5])]:
 try:a.allocate(t,w)
 except ValueError:pass
 else:raise AssertionError((t,w))
print('ORACLE_CASES',count)
'''
    with tempfile.TemporaryDirectory(prefix='helix-luna-grade-') as tmp:
        for name in ('allocation.py','test_allocation.py'):shutil.copyfile(cwd/name,Path(tmp)/name)
        result=subprocess.run([sys.executable,'-c',script],cwd=tmp,capture_output=True,text=True,timeout=30)
    kd.save(cwd.parent/(cwd.name+'-caller-grade.json'),{'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert result.returncode==0,result.stderr
    return {'independent_allocation_oracle':'PASS','stdout':result.stdout}


def run(root):
    root=Path(root);m=json.loads((root/'manifest.json').read_text());state=root/'results.json'
    if state.exists():raise ValueError('No retry')
    r={'state':'RUNNING','rows':[],'manifest_sha256':kd.sha(root/'manifest.json')};kd.save(state,r)
    try:
        for case,arm in m['order']:
            verify(m);cwd=root/case/arm
            kd.research_session.RPC=kd.rpc_with_base(Path(m['kernel']) if arm=='helix' else None)
            try:
                with kd.research_session.Session(m['model'],cwd,root/(case+'-'+arm+'-run'),
                        cwd/'.agents/skills/helixcontext/SKILL.md' if arm=='helix' else None) as s:
                    answer,turn=s.turn((cwd/'prompt.txt').read_text());row={'case':case,'arm':arm,'answer':answer,'usage':s.total,'turn':turn}
            finally:kd.research_session.RPC=kd.OriginalRPC
            r['rows'].append(row);kd.save(state,r);verify(m)
            row['checks']=grade(root,case,cwd,answer);kd.save(state,r)
        r['state']='AWAITING_TRACE_AUDIT';kd.save(state,r)
    except BaseException as exc:
        r.update(state='STOPPED_PENDING_AUDIT',error=str(exc));kd.save(state,r);raise


if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
