"""Replay actual generated supplemental tests; not counterfactual model decisions."""
import hashlib,json,shlex,subprocess,sys,tempfile
from pathlib import Path
import audit,caller_patch_pair

def sha(b):return hashlib.sha256(b).hexdigest()
def run(root,out):
    root=Path(root);suites={};provenance={}
    for arm in ('on','off'):
        p=root/arm/'receipts/run';status=json.loads((p/'status.json').read_text())
        raw=(p/'native-events.jsonl').read_bytes();assert sha(raw)==status['native_events_sha256']
        es=[json.loads(l) for l in raw.splitlines()]
        if arm=='off':
            changes=[c for e in es if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='fileChange' for c in e['params']['item']['changes'] if c['path'].endswith('/extra_checks.py')]
            assert len(changes)==1;suites[arm]=changes[0]['diff'];provenance[arm]={'native_events_sha256':sha(raw),'extraction':'Exact fileChange addition extra_checks.py','suite_sha256':sha(suites[arm].encode())}
        else:
            cmds=[e['params']['item']['command'] for e in es if e.get('method')=='item/completed' and e.get('params',{}).get('item',{}).get('type')=='commandExecution']
            cmd=next(c for c in cmds if 'class LegacySequence:' in c);shell=shlex.split(cmd)[-1]
            start=shell.index("ns={};exec(Path(");end=shell.index("binding=json.loads",start)
            body=shell[start:end]
            old="Path('.evidence/review-attempts/proposal/queue_state.py')";assert body.count(old)==1
            suites[arm]='from pathlib import Path\n'+body.replace(old,"Path('queue_state.py')")
            provenance[arm]={'native_events_sha256':sha(raw),'command_sha256':sha(cmd.encode()),'extraction':'Exact semantic slice ns={} through before binding=json.loads; import Path and local source path adaptation only','slice_sha256':sha(body.encode()),'suite_sha256':sha(suites[arm].encode())}
    variants={'reference':audit.GOOD,
        'shared_initial_list':audit.GOOD.replace('class Queue:\n','class Queue:\n    shared=[]\n').replace('self.items=[]','self.items=Queue.shared'),
        'stale_cursor':audit.GOOD.replace('self.cursor=len(self.items)','self.cursor+=len(pending)'),
        'self_alias_noop':audit.GOOD.replace('        pending=[]','        if values is self.items: return self.cursor\n        pending=[]'),
        'bool_accepted':audit.GOOD.replace('type(value) is not int','not isinstance(value,int)')}
    results={}
    for name,source in variants.items():
        row={}
        with tempfile.TemporaryDirectory(prefix='helix-test-strength-') as tmp:
            d=Path(tmp);(d/'queue_state.py').write_text(source)
            for arm,script in {**suites,'declared':caller_patch_pair.checker()}.items():
                (d/'probe.py').write_text(script)
                p=subprocess.run([sys.executable,'-B','probe.py','queue_state.py'],cwd=d,capture_output=True,text=True,timeout=30)
                row[arm]={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        results[name]=row
    assert all(v['exit_code']==0 for v in results['reference'].values())
    # Explicit contract witness, independent of generated test content.
    ns={};exec(variants['shared_initial_list'],ns);a=ns['Queue']();a.append_batch([7]);b=ns['Queue']()
    assert b.items==[7], 'Mutant must violate initially empty per-instance state'
    result={'classification':'Posthoc development test-coverage audit, not native mutant verdicts or model intelligence comparison','provenance':provenance,'results':results,'shared_list_witness':'Construct a; append [7]; construct b; observed b.items=[7] rather than initially empty.','native_calls':0,'script_sha256':sha(Path(__file__).read_bytes())}
    Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:{a:v['exit_code'] for a,v in row.items()} for k,row in results.items()},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
