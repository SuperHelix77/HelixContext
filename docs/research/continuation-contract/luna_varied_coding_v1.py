"""Three prospective known-to-researcher coding pairs; no adaptive profile edits.

Both arms receive actual caller memory preflight. The composite candidate uses
the frozen V7 base, native-attached skill, supplied source and checked realization.
This is a research caller, not a production app adapter or a new semantic policy.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'engine/output'))
import observed_session
import caller_memory_receipt as memory
import caller_registration
from app_server_native import usage
from varied_coding_tasks import TASKS

BASE=REPO/'engine/profiles/luna-coding-v1-75/base.md'
BASE_HASH='f07e19dbe57d410b23524332acf30c0f19650ab631f9e654897cbf440c61c4c0'
DEFAULT_HASH='a91357a1cd2727a0be06d461248d6e3a7274746e38108f548a3adf2cc2430415'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def prepare(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    assert sha(BASE)==BASE_HASH
    files=[Path(__file__),HERE/'varied_coding_tasks.py',BASE,REPO/'engine/profiles/luna-coding-v1-75/profile.json',
           Path(observed_session.__file__),Path(memory.__file__),Path(caller_registration.__file__),memory.CLIENT,
           REPO/'engine/output/app_server_native.py',REPO/'engine/output/raw_receipts.py',
           Path('/Users/mert/.codex/AGENTS.md'),Path('/Users/mert/.codex/config.toml')]
    m={'model':'gpt-5.6-luna','effort':'high','base_file':str(BASE),'cases':list(TASKS),
       'max_semantic_turns':2,'blind_retries':0,'order':[], 'inputs':{},
       'classification':'Three prospective researcher-authored single-module repairs; frozen profile; matched caller memory preflight; development, not population holdout',
       'boundary':'Default-base native tools vs frozen V7/native-attached skill/source-only/caller mechanics; Engine active, ordinary tools and semantic re-entry retained',
       'stop':'No retry or profile adjustment. Retain behavioral failures and finish prespecified independent pairs. Stop on infrastructure/binding/raw receipt failure.',
       'limits':['No general parity proof','Caller execution outside native workspace sandbox','One-file publication has no uncooperative-writer isolation','Two semantic turns is an experiment bound, not a product policy','Full physical I/O, research and parent-agent cost unmetered']}
    for case,spec in TASKS.items():
        taskroot=root/case;taskroot.mkdir()
        data={'task':spec['task'],'files':{'solution.py':spec['module'],'test_solution.py':spec['tests'],'settings.json':'{"version":1,"protected":true}\n'}}
        save(taskroot/'source.json',data);files.append(taskroot/'source.json')
        order=['off','on'];secrets.SystemRandom().shuffle(order);m['order'] += [[case,a] for a in order]
        for arm in ('off','on'):
            cwd=taskroot/arm;cwd.mkdir()
            for name,text in data['files'].items():(cwd/name).write_text(text)
            skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True)
            skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes());files.append(skill)
            (cwd/'AGENTS.md').write_text(memory.LOCAL_RULE)
            common='Work only in this task directory. Other runs, solutions and evaluators are out of scope. Ordinary tools and semantic review remain available.\n'+spec['task']
            if arm=='on':
                common+='''
Caller execution: return only the complete replacement Python module. Caller stages these exact bytes, runs the existing unittest suite and independent contract checks, and publishes solution.py only if checks pass and protected inputs are unchanged. Leave the original files unchanged for caller publication. Checks and publication are pending mechanics, not unresolved semantics. Caller reports actual results; do not claim tests ran before they do. If semantic information is missing, return {"semantic_obligations":["question"]} instead. You retain implementation, semantic review, test-adequacy judgment and ordinary tools for any needed probes. Failed checks return new evidence for reconsideration.
Exact files:
'''+json.dumps(data['files'],ensure_ascii=False)
            mem=taskroot/(arm+'-memory')
            memory.prepare(cwd,common,case+' coding function contract repair',mem)
            prompt=memory.attach(cwd,common,mem,sha(mem/'receipt.json'))
            p=taskroot/(arm+'-prompt.txt');p.write_text(prompt);files.append(p)
            files += list(mem.iterdir())
            for name in ('test_solution.py','settings.json','AGENTS.md'):files.append(cwd/name)
            m['inputs'][case+'/'+arm]={n:sha(cwd/n) for n in data['files']}
    m['sha256']={str(p.resolve()):sha(p) for p in files};save(root/'manifest.json',m)
    print(json.dumps({'manifest_sha256':sha(root/'manifest.json'),'order':m['order']}))


def verify(m):
    for name,digest in m['sha256'].items():
        if sha(name)!=digest:raise RuntimeError('Bound source changed: '+name)


def verify_initial(root,m,case,arm):
    verify(m)
    for name,digest in m['inputs'][case+'/'+arm].items():
        if sha(root/case/arm/name)!=digest:raise RuntimeError('Initial source changed: '+name)


def source(text):
    import ast
    text=text.strip()
    if text.startswith('```python\n') and text.endswith('```'):text=text[10:-3]
    elif text.startswith('```\n') and text.endswith('```'):text=text[4:-3]
    ast.parse(text)
    if text.lstrip().startswith('{'):raise ValueError('Semantic questions/schema require caller attention')
    return text.encode()+(b'' if text.endswith('\n') else b'\n')


def grade(case,cwd,receipt):
    begin=time.perf_counter()
    result=subprocess.run([sys.executable,'-B',str(HERE/'varied_coding_tasks.py'),case,str(cwd)],cwd=cwd,capture_output=True,text=True,timeout=40)
    data={'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'caller_seconds':time.perf_counter()-begin}
    if result.returncode==0:data['checks']=json.loads(result.stdout)
    save(receipt,data);return data


def realize(root,m,case,raw,index):
    verify_initial(root,m,case,'on');stage=root/case/('stage-'+str(index));stage.mkdir()
    (stage/'solution.py').write_bytes(raw)
    for name in ('test_solution.py','settings.json'):shutil.copyfile(root/case/'on'/name,stage/name)
    pinned={p.name:sha(p) for p in stage.iterdir()};begin=time.perf_counter()
    result=grade(case,stage,root/case/('on-check-'+str(index)+'.json'))
    assert all(sha(stage/n)==h for n,h in pinned.items()), 'Checker mutated staged inputs'
    verify_initial(root,m,case,'on')
    if result['exit_code']==0:
        pending=root/case/'on/caller-pending.py';pending.write_bytes(raw)
        verify_initial(root,m,case,'on');os.replace(pending,root/case/'on/solution.py')
        assert sha(root/case/'on/solution.py')==pinned['solution.py']
    return {**result,'source_sha256':pinned['solution.py'],'published':result['exit_code']==0,'completion_seconds':time.perf_counter()-begin}


def run(root):
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());path=root/'results.json'
    if path.exists():raise ValueError('No retry')
    result={'state':'RUNNING','rows':[],'manifest_sha256':sha(root/'manifest.json')};save(path,result)
    original=observed_session.RPC
    class KernelRPC(original):
        def call(self,method,params):
            if method=='thread/start':params={**params,'config':{**params['config'],'model_instructions_file':str(BASE)}}
            return super().call(method,params)
    try:
        for case,arm in m['order']:
            verify_initial(root,m,case,arm);cwd=root/case/arm
            observed_session.RPC=KernelRPC if arm=='on' else original
            row={'case':case,'arm':arm,'turns':[]};result['rows'].append(row);save(path,result)
            with observed_session.Session(m['model'],cwd,root/case/(arm+'-run'),cwd/'.agents/skills/helixcontext/SKILL.md' if arm=='on' else None) as session:
                prompt=caller_registration.attach(session,(root/case/(arm+'-prompt.txt')).read_text())
                for index in range(1,(m['max_semantic_turns'] if arm=='on' else 1)+1):
                    answer,turn=session.turn(prompt);current={'answer':answer,'native':turn};row['turns'].append(current)
                    row['usage']=dict(session.total);save(path,result)
                    if arm=='off':
                        verify(m);row['completion']=grade(case,cwd,root/case/'off-check.json');break
                    try:raw=source(answer)
                    except (ValueError,SyntaxError) as exc:
                        row['completion']={'exit_code':None,'semantic_attention_required':str(exc)};break
                    completion=realize(root,m,case,raw,index);current['completion']=completion;row['completion']=completion;save(path,result)
                    if completion['exit_code']==0:break
                    prompt='Caller has not published. Reassess these exact check failures and return a replacement module or unresolved semantic questions.\n'+json.dumps(completion)
            if session.failed:raise RuntimeError('Native/raw capture failed')
            row['raw_capture']=session.capture_status;row['finite_checks']='PASS' if row['completion']['exit_code']==0 else 'FAIL'
            verify(m);save(path,result)
            print(json.dumps({'case':case,'arm':arm,'usage':row['usage'],'finite_checks':row['finite_checks']}),flush=True)
        result['state']='AWAITING_AUDIT';save(path,result)
    except BaseException as exc:
        result.update(state='STOPPED_PENDING_AUDIT',error=repr(exc));save(path,result);raise
    finally:observed_session.RPC=original


def audit(root):
    from statistics import median
    root=Path(root).resolve();m=json.loads((root/'manifest.json').read_text());verify(m)
    result=json.loads((root/'results.json').read_text());assert result['state']=='AWAITING_AUDIT'
    rows=[]
    for row in result['rows']:
        case,arm=row['case'],row['arm'];run=root/case/(arm+'-run');status=json.loads((run/'status.json').read_text())
        assert status['state']=='closed' and status['model']==m['model'] and status['effort']=='high'
        assert sha(run/'native-events.jsonl')==status['native_events_sha256']
        events=[json.loads(l) for l in (run/'native-events.jsonl').read_text().splitlines()]
        updates=[e for e in events if e.get('method')=='thread/tokenUsage/updated']
        assert usage(updates[-1])==status['usage']==row['usage']
        for key,native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates)==status['usage'][key]
        raw=(run/'raw/raw-rollout.jsonl').read_bytes();idx=json.loads((run/'raw/raw-tool-index.json').read_text())
        assert hashlib.sha256(raw).hexdigest()==idx['sha256']==status['raw_capture']['sha256']
        for record in idx['records']:assert hashlib.sha256(raw[record['start']:record['end']]).hexdigest()==record['line_sha256']
        meta=next(json.loads(l)['payload'] for l in raw.splitlines() if json.loads(l).get('type')=='session_meta')
        base=meta['base_instructions']['text'].encode()
        if arm=='on':
            assert base==BASE.read_bytes()[:-1] and meta['base_instructions']['provenance']['type']=='custom'
            if row['finite_checks']=='PASS':assert source(row['turns'][-1]['answer'])==(root/case/arm/'solution.py').read_bytes()
        else:assert hashlib.sha256(base).hexdigest()==DEFAULT_HASH
        # Regrade the exact published source; preserve original check receipts.
        check=grade(case,root/case/arm,root/case/(arm+'-audit-check.json'))
        assert (check['exit_code']==0)==(row['finite_checks']=='PASS')
        mem=json.loads((root/case/(arm+'-memory')/'receipt.json').read_text())
        rows.append({'case':case,'arm':arm,'usage':row['usage'],'native_sha256':status['native_events_sha256'],
                     'raw_sha256':idx['sha256'],'raw_bytes':idx['bytes'],'raw_tool_calls':idx['calls'],'segments':len(updates),'turns':len(status['turns']),
                     'source_sha256':sha(root/case/arm/'solution.py'),'checks':check.get('checks'),'finite_checks':row['finite_checks'],
                     'elapsed_seconds':status['elapsed_seconds'],'memory_seconds':mem['elapsed_seconds'],'memory_raw_bytes':mem['raw_bytes'],
                     'caller_check_seconds':sum(t.get('completion',{}).get('completion_seconds',0) for t in row['turns'])})
    pairs=[]
    for case in m['cases']:
        a=next(r for r in rows if r['case']==case and r['arm']=='off');b=next(r for r in rows if r['case']==case and r['arm']=='on')
        savings={k:100*(1-b['usage'][k]/a['usage'][k]) for k in ('input_tokens','output_tokens')}
        savings['uncached_input_tokens']=100*(1-(b['usage']['input_tokens']-b['usage']['cached_input_tokens'])/(a['usage']['input_tokens']-a['usage']['cached_input_tokens']))
        pairs.append({'case':case,'savings_percent':savings,'finite_checks':'PASS' if a['finite_checks']==b['finite_checks']=='PASS' else 'FAIL','meets_75_75':min(savings['input_tokens'],savings['output_tokens'])>=75,'meets_80_80':min(savings['input_tokens'],savings['output_tokens'])>=80})
    report={'classification':m['classification'],'manifest_sha256':sha(root/'manifest.json'),'rows':rows,'pairs':pairs,
            'median_savings_percent':{k:median(p['savings_percent'][k] for p in pairs) for k in pairs[0]['savings_percent']},
            'native_usage_all_attempts':{k:sum(r['usage'][k] for r in rows) for k in rows[0]['usage']},
            'N':len(pairs),'finite_checks':'PASS' if all(p['finite_checks']=='PASS' for p in pairs) else 'FAIL',
            'general_release':False,'limits':m['limits'],'native_control':'Matched-memory-preflight default base with ordinary tools; not raw desktop economics'}
    save(root/'audit.json',report);save(HERE/'LUNA_VARIED_CODING_V1_RESULT.json',report)
    print(json.dumps({'pairs':pairs,'median':report['median_savings_percent']}))


if __name__=='__main__':{'prepare':prepare,'run':run,'audit':audit}[sys.argv[1]](sys.argv[2])
