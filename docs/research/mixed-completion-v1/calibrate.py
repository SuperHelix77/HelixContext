"""Offline mixed-state and real native-format replay, no new model requests."""
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'engine/prototype'))
from evidence import Store
from workflow_memory import Memory,encode
from completion_ledger import CompletionLedger,EMPTY
from mixed_workflow import MixedWorkflow,next_action,VERSION


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def make_event(n,request=None):
    return encode({'turn':n,'event_id':f'E{n:02d}','data':{'old_label':'cafe\u0301 / Ω / 箱\t  ','seq':'000042'},
        'request':request or f'Record this event for the ongoing workflow. Reply ACK E{n:02d}. No other action is requested at this turn.'})


def capture(text,turn):
    return b'\n'.join(encode(x) for x in [
        {'method':'item/completed','params':{'threadId':'SCRIPTED','turnId':turn,'item':{'id':'answer-'+turn,'type':'agentMessage','phase':'final_answer','text':text}}},
        {'method':'turn/completed','params':{'threadId':'SCRIPTED','turn':{'id':turn,'status':'completed'}}}])+b'\n'


def run(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    store=Store(root/'mixed');initial=store.put(encode({'established_facts':[],'open_questions':[]}))
    flow=MixedWorkflow(CompletionLedger(Memory(store)),'mixed50','a'*64,initial)
    head=EMPTY;raws=[];answers=[];per_append=[]
    for n in range(1,51):
        then=time.perf_counter();before=dict(store.metrics)
        semantic=n in [12,25,38,50]
        raw=make_event(n,'SCRIPTED semantic checkpoint; requires real model in live use.' if semantic else None)
        if semantic:
            answer=f'SCRIPTED ordinary response at checkpoint {n}; no capability claim.\n'
            ref=store.put(capture(answer,f'T{n}'))
            state=store.put(encode({'established_facts':['scripted'], 'open_questions':['unresolved'], 'checkpoint':n}))
            r=flow.record_model(raw,ref,thread_id='SCRIPTED',turn_id=f'T{n}',after_state=state,
                expected_head=head,binding='b'*64,current_binding=lambda:'b'*64)
        else:r=flow.record_ack(raw,expected_head=head,binding='b'*64,current_binding=lambda:'b'*64)
        head=r['head'];raws.append(raw);answers.append(r['answer'])
        per_append.append({'event':n,'owner':r['answer_owner'],'seconds':time.perf_counter()-then,
                           'store_delta':{k:store.metrics[k]-before[k] for k in before}})
    append_metrics=dict(store.metrics)
    restarted_store=Store(root/'mixed');restart=MixedWorkflow(CompletionLedger(Memory(restarted_store)),'mixed50','a'*64,initial)
    recovered=restart.recover(head)
    assert [x['event_bytes'] for x in recovered]==raws
    assert [x['answer_bytes'] for x in recovered]==answers
    assert len(recovered)==50 and sum(x['answer_owner']=='model' for x in recovered)==4
    # A previously unselected early field remains exact despite later checkpoints.
    older=json.loads(recovered[0]['event_bytes'])['data']
    assert older['old_label']=='cafe\u0301 / Ω / 箱\t  ' and older['seq']=='000042'
    late=flow.record_ack(raws[0],expected_head=head,binding='b'*64,current_binding=lambda:'b'*64)
    assert late['replayed'] and late['head']==head and late['current_state']==recovered[-1]['after_state']
    native_root=Path('/Users/mert/Documents/ChatGPT/Helix/research/astra-cold-full-final-v1-20260910')
    audit=read(REPO/'docs/research/cold-native-final-v1/AUDIT.json')
    fixture=read(native_root/'fixture.json');real=[]
    for row in audit['rows']:
        arm=row['arm'];folder=native_root/(arm+'-run');native=folder/'native-events.jsonl';final=folder/'turn-1-answer.txt'
        assert sha(native)==row['native_sha256'] and sha(final)==row['final_sha256']
        status=read(folder/'status.json');assert status['state']=='closed'
        s=Store(root/('native-'+arm));state=s.put(encode({'task':fixture['task'],'source_sha256':sha(native_root/arm/'history.json')}))
        f=MixedWorkflow(CompletionLedger(Memory(s)),'actual-cold-'+arm,'c'*64,state)
        ref=s.put(native.read_bytes());raw=make_event(1,fixture['task'])
        r=f.record_model(raw,ref,thread_id=status['thread_id'],turn_id=status['turns'][0]['turn_id'],
                        after_state=state,expected_head=EMPTY,binding='d'*64,current_binding=lambda:'d'*64)
        assert r['answer']==final.read_bytes()
        assert f.recover(r['head'])[0]['answer_bytes']==final.read_bytes()
        real.append({'arm':arm,'native_sha256':sha(native),'final_sha256':sha(final),
            'unchanged_native_final':'PASS','head':r['head'],'store_io':dict(s.metrics),
            'scope':'Replay of prior audited native stream; no new task or inference; task-state metadata is caller evidence, not semantic certification'})
    paths=[Path(__file__),REPO/'engine/prototype/mixed_workflow.py',REPO/'engine/prototype/test_mixed_workflow.py']
    paths += [REPO/'engine/prototype'/n for n in ['evidence.py','workflow_memory.py','completion_ledger.py','passive_workflow.py','semantic_execution.py']]
    report={'version':VERSION,'classification':'OFFLINE_LIFECYCLE_CANDIDATE; not an economic/capability release',
        'new_native_calls':0,'scripted_events':50,'scripted_semantic_checkpoints':4,'caller_owned_acks':46,
        'exact_order_answer_state_recovery':'PASS','late_replay_does_not_roll_back_state':'PASS',
        'latent_old_field_exact_recovery':'PASS; retrieval only, no new model reasoning about late relevance',
        'append_io':append_metrics,'restart_io':dict(restarted_store.metrics),'per_append':per_append,
        'native_format_replays':real,'seconds':time.perf_counter()-start,
        'source_bindings':{str(p.relative_to(REPO)):sha(p) for p in paths},
        'cost_limits':'Logical instrumented Store bytes and wall time; other Python/SQLite reads, metadata, physical I/O and full CPU energy unmeasured. Current ledger revalidates the prefix; quadratic long-run cost retained.',
        'release_gaps':['Caller must bind event/state to actual native request and persist in-flight handle before invoking; completion adapter alone does not do this.',
                        'No exactly-once external effects or consumer acknowledgement implementation.',
                        'No Codex app pre-inference hook activated.',
                        'No mixed semantic task suite, semantic grader or native economic pair qualified.']}
    save(root/'RESULT.json',report)
    print(json.dumps({k:report[k] for k in ['new_native_calls','scripted_events','exact_order_answer_state_recovery','seconds','append_io','restart_io']}))


if __name__=='__main__':run(sys.argv[1])
