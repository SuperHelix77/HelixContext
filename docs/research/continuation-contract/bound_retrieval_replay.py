"""Offline authority-bound Engine execution against retained retrieval/cold fixtures.

No model is run. Historical native controls are provenance, not a fresh pair.
"""
import json,sys,time
from pathlib import Path
import luna_capability_pair as cap
import resolved_retrieval as resolved
import bound_retrieval as gate
from evidence import Store


def run(root,prior):
    root=Path(root).resolve();prior=Path(prior).resolve();root.mkdir(parents=True,exist_ok=False)
    rows=[]
    for case in ('selection','cold'):
        spec=json.loads((prior/(case+'-source.json')).read_text())
        data=spec['records'] if case=='selection' else spec['events'][:-1]
        task=spec['task'] if case=='selection' else spec['events'][-1]['request']
        source_path=prior/case/'default'/('records.json' if case=='selection' else 'history.json')
        case_dir=root/case;case_dir.mkdir();store=Store(case_dir/'store');started=time.perf_counter()
        raw=source_path.read_bytes()
        original_manifest=json.loads((prior/'manifest.json').read_text())
        assert resolved.hashlib.sha256(raw).hexdigest()==original_manifest['sha256'][str(source_path)]
        assert json.loads(raw)==data
        ref=store.put(raw)
        # Reopen the store before retrieval; the source remains cold by hash.
        reopened=Store(case_dir/'store')
        def no_semantic_call(*args):raise AssertionError('Recognized task unexpectedly needs inference')
        state={'schema':gate.VERSION,'adapter_version':resolved.VERSION,'task_sha256':resolved.hashlib.sha256(task.encode()).hexdigest(),'source_ref':ref,'active_constraints':[]}
        state_path=case_dir/'task-state.json'
        state_path.write_text(json.dumps(state,sort_keys=True)+'\n')
        expected_root=gate.state_root(state)
        result=gate.dispatch(task,reopened,ref,expected_state_root=expected_root,current_state=lambda:json.loads(state_path.read_text()),semantic=no_semantic_call)
        assert result['state']=='RESOLVED' and result['model_calls']==0
        answer=json.dumps(result['answer'],ensure_ascii=False,separators=(',',':'))
        checks=cap.grade(prior,case,prior/case/'default',answer)
        (case_dir/'answer.json').write_text(answer+'\n')
        s=json.loads((prior/(case+'-default-run')/'status.json').read_text())
        native=prior/(case+'-default-run')/'native-events.jsonl'
        assert cap.kd.sha(native)==s['native_events_sha256'] and s['state']=='closed'
        payload=sum(len(x.encode()) for x in result['answer'].values() if isinstance(x,str))
        row={'case':case,'execution':'Engine-only recognized request; no model invocation','checks':checks,'engine_active':True,'model_calls':0,'state_root':expected_root,'state_file_sha256':cap.kd.sha(state_path),'state_bytes_written':state_path.stat().st_size,'model_input_tokens':0,'model_output_tokens':0,'source_path':str(source_path),'original_native_input_bytes_preserved':True,'source_ref':ref,'answer_sha256':cap.kd.sha(case_dir/'answer.json'),'answer_bytes':len((answer+'\n').encode()),'elapsed_seconds':time.perf_counter()-started,'ingest_store_io':store.metrics,'recovery_store_io':reopened.metrics,'retained_control_usage':s['usage'],'retained_control_native_sha256':s['native_events_sha256'],'task_sha256':resolved.hashlib.sha256(task.encode()).hexdigest()}
        rows.append(row)
    report={'classification':'Offline deterministic execution replay, not a native paired model benchmark','model_capability_replication':False,'gate_sha256':cap.kd.sha(Path(gate.__file__)),'production_codex_app_integration':False,'rows':rows,'mechanism_sha256':cap.kd.sha(Path(resolved.__file__)),'runner_sha256':cap.kd.sha(Path(__file__)),'limits':['Caller must supply complete task authority; this replay explicitly has no inherited task constraints','Concurrent external delivery still requires compare-and-swap on the returned state root','Only two exact parameterized request grammars; unrecognized forms need semantic execution','Zero inference is observed for these compiled tasks, not a universal model saving','Research implementation and full physical/system I/O costs are unmetered','Cold task is a history snapshot, not forty live turns']}
    cap.kd.save(root/'result.json',report)
    Path(__file__).with_name('BOUND_RETRIEVAL_REPLAY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('case','model_calls','checks','elapsed_seconds','answer_bytes')} for r in rows]))


if __name__=='__main__':run(*sys.argv[1:])
