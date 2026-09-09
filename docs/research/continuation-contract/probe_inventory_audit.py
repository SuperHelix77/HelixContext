"""Posthoc finite-suite mutation replay; no native calls or capability claims."""
import hashlib,json,shlex,subprocess,sys,tempfile,time
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def run(root,out):
    root=Path(root);d=root/'on';p=d/'receipts/run'
    status=json.loads((p/'status.json').read_text());raw=(p/'events.jsonl').read_bytes()
    assert sha(raw)==status['events_sha256']
    es=[json.loads(l) for l in raw.splitlines()]
    commands=[e['item']['command'] for e in es if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    command=next(c for c in commands if 'class HostileInt' in c)
    shell=shlex.split(command)[-1];script=shell.split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
    good=(d/'proposal.py').read_text()
    variants={'reference':good,
        'shared_storage':good.replace('class Queue:\n','class Queue:\n    shared=[]\n').replace('self.items=[]','self.items=Queue.shared'),
        'self_alias_noop':good.replace('        pending=[]','        if values is self.items: return self.cursor\n        pending=[]'),
        'huge_int_rejected':good.replace('value<0','value<0 or value>2**63-1'),
        'legacy_sequence_rejected':good.replace('        pending=[]',"        if not hasattr(values,'__iter__'): raise TypeError('iterator required')\n        pending=[]"),
        'input_length_hint_used':good.replace('        pending=[]',"        import operator\n        operator.length_hint(values)\n        pending=[]"),
        'untested_value_dropped':good.replace('            pending.append(value)','            if value != 4093: pending.append(value)')}
    suites={'declared':(d/'check.py').read_text(),'independence':(d/'check_independence.py').read_text(),'astra_supplemental':script}
    result={'classification':'POSTHOC finite-suite coverage; not native decisions, holdout or capability parity','native_calls':0,'provenance':{'events_sha256':sha(raw),'command_sha256':sha(command.encode()),'extraction':'Unchanged Python heredoc from completed semantic-probe command; supplied proposal varied in private temporary directories only','suite_hashes':{k:sha(v.encode()) for k,v in suites.items()}},'results':{}}
    for name,source in variants.items():
        rows={}
        for suite,body in suites.items():
            with tempfile.TemporaryDirectory(prefix='helix-probe-inventory-') as tmp:
                t=Path(tmp)
                for rel in ('CONTRACT.md','check.py','check_independence.py'):(t/rel).write_bytes((d/rel).read_bytes())
                (t/'proposal.py').write_text(source);(t/'queue_state.py').write_text(source);(t/'probe.py').write_text(body)
                start=time.perf_counter();r=subprocess.run([sys.executable,'-B','probe.py','queue_state.py'],cwd=t,capture_output=True,text=True,timeout=30)
                rows[suite]={'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.perf_counter()-start}
        result['results'][name]={'source_sha256':sha(source.encode()),'suites':rows}
    assert all(r['exit_code']==0 for r in result['results']['reference']['suites'].values())
    assert all(r['exit_code']==0 for r in result['results']['untested_value_dropped']['suites'].values())
    ns={};exec(variants['untested_value_dropped'],ns);q=ns['Queue']();observed=q.append_batch([4093]);assert observed==0 and q.items==[]
    result['independent_gap_witness']={'input':[4093],'required_items':[4093],'observed_items':q.items,'required_return':1,'observed_return':observed,'all_existing_suites_pass':True}
    result['script_sha256']=sha(Path(__file__).read_bytes());Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{s:v['exit_code'] for s,v in row['suites'].items()} for k,row in result['results'].items()},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
