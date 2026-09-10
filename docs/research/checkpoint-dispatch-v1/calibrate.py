"""Replay real request/capture formats and read an existing native thread; no inference."""
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
sys.path[:0]=[str(REPO/'engine/output'),str(REPO/'engine/prototype')]
from app_server_native import RPC,CLI
from checkpoint_dispatch import Journal,BoundSend,commit_capture
from evidence import Store
from workflow_memory import Memory,encode
from completion_ledger import CompletionLedger,EMPTY
from mixed_workflow import MixedWorkflow


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')


def run(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);started=time.perf_counter()
    native_root=Path('/Users/mert/Documents/ChatGPT/Helix/research/astra-cold-full-final-v1-20260910')
    audit=read(REPO/'docs/research/cold-native-final-v1/AUDIT.json');fixture=read(native_root/'fixture.json')
    config=Path('/Users/mert/.codex/config.toml');initial_config=sha(config)
    rows=[]
    for row in audit['rows']:
        arm=row['arm'];folder=native_root/(arm+'-run');native=folder/'native-events.jsonl'
        assert sha(native)==row['native_sha256']
        lines=(folder/'requests.jsonl').read_bytes().splitlines(keepends=True)
        actual=[(l,json.loads(l)) for l in lines if json.loads(l).get('method')=='turn/start']
        assert len(actual)==1;wire_raw,wire=actual[0]
        native_bytes=native.read_bytes();reply=next(json.loads(l) for l in native_bytes.splitlines() if json.loads(l).get('id')==wire['id'] and 'method' not in json.loads(l))
        store=Store(root/arm/'evidence');state=store.put(encode({'task':fixture['task'],'source_sha256':sha(native_root/arm/'history.json')}))
        flow=MixedWorkflow(CompletionLedger(Memory(store)),arm,'a'*64,state)
        raw_event=encode({'turn':1,'event_id':'E01','data':{'source_sha256':sha(native_root/arm/'history.json')},'request':fixture['task']})
        j=Journal(root/arm/'journal');binding=hashlib.sha256(encode([initial_config,state])).hexdigest()
        ref=j.prepare(workflow=flow.scope,event_id='E01',event_bytes=raw_event,pre_head=EMPTY,
            pre_state=state,expected_request=wire['params'],expected_rpc_id=wire['id'],binding=binding)
        # Exercise the actual RPC.call method without constructing a process or
        # contacting a model. The recorded request must leave the hook unchanged.
        rpc=object.__new__(RPC);rpc.next_id=wire['id']-1;sent=[]
        rpc.send=lambda x:sent.append((json.dumps(x,separators=(',',':'))+'\n').encode())
        rpc.read=lambda:reply
        before=time.perf_counter()
        with BoundSend(rpc,j,ref,lambda:binding):result=rpc.call('turn/start',wire['params'])
        assert result==reply['result'] and sent==[wire_raw]
        committed=commit_capture(flow,j,ref,native_bytes,after_state=state,current_binding=lambda:binding)
        assert committed['answer']==(folder/'turn-1-answer.txt').read_bytes()
        assert hashlib.sha256(committed['answer']).hexdigest()==row['final_sha256']
        restarted=Journal(j.root)
        replay=commit_capture(flow,restarted,ref,native_bytes,after_state=state,current_binding=lambda:binding)
        assert replay['replayed'] and replay['head']==committed['head']
        try:restarted.send_once(ref,wire,lambda _:sent.append(b'BAD_RETRY'),current_binding=lambda:binding)
        except FileExistsError:pass
        else:raise AssertionError('Duplicate send admitted')
        assert sent==[wire_raw]
        rows.append({'arm':arm,'wire_sha256':hashlib.sha256(wire_raw).hexdigest(),
            'request_parameters_unchanged':'PASS','native_sha256':sha(native),'final_sha256':row['final_sha256'],
            'real_rpc_call_replay':'PASS','exact_final_after_restart':'PASS','duplicate_send_blocked':'PASS',
            'new_native_calls':0,'seconds':time.perf_counter()-before,'journal_bytes':sum(p.stat().st_size for p in j.root.rglob('*') if p.is_file()),
            'store_io':dict(store.metrics),'ticket':ref})
    # Read-only recovery of a known persisted thread using supported paginated
    # methods. No thread/start, turn/start, resume or model invocation is sent.
    folder=native_root/'on-run';status=read(folder/'status.json');out=root/'readback';out.mkdir()
    rpc=RPC(native_root/'on',out,'gpt-6-astra');read_started=time.perf_counter()
    try:
        rpc.call('initialize',{'clientInfo':{'name':'helix-readback-check','version':'1'},'capabilities':{'experimentalApi':True}})
        rpc.send({'method':'initialized'})
        meta=rpc.call('thread/read',{'threadId':status['thread_id'],'includeTurns':False})
        save(out/'thread.json',meta)
        turns=rpc.call('thread/turns/list',{'threadId':status['thread_id'],'limit':1,'sortDirection':'desc','itemsView':'notLoaded'})
        save(out/'turns.json',turns)
        assert len(turns['data'])==1 and turns['data'][0]['id']==status['turns'][0]['turn_id']
        items=rpc.call('thread/items/list',{'threadId':status['thread_id'],'turnId':status['turns'][0]['turn_id'],'limit':8,'sortDirection':'desc'})
        save(out/'items.json',items)
        entries=[x.get('item',x) for x in items['data']]
        finals=[x for x in entries if x.get('type')=='agentMessage' and x.get('phase')=='final_answer']
        assert len(finals)==1 and finals[0]['text']==(folder/'turn-1-answer.txt').read_text()
    finally:rpc.close()
    requests=[json.loads(l) for l in (out/'requests.jsonl').read_bytes().splitlines()]
    assert not any(x.get('method') in ['thread/start','thread/resume','turn/start'] for x in requests)
    assert sha(config)==initial_config
    report={'classification':'OFFLINE_WIRE_REPLAY_PLUS_READ_ONLY_NATIVE_RECOVERY; no new model benchmark',
        'new_native_calls':0,'rows':rows,'persisted_thread_readback':{'state':'PASS','thread_id':status['thread_id'],
            'turn_id':status['turns'][0]['turn_id'],'final_sha256':sha(folder/'turn-1-answer.txt'),
            'methods':[x['method'] for x in requests if 'method' in x],'seconds':time.perf_counter()-read_started,
            'native_wire_bytes':(out/'native-events.jsonl').stat().st_size,'global_config_unchanged':True},
        'seconds':time.perf_counter()-started,'source_bindings':{str(p.relative_to(REPO)):sha(p) for p in [Path(__file__),REPO/'engine/output/checkpoint_dispatch.py',REPO/'engine/output/test_checkpoint_dispatch.py',REPO/'engine/output/app_server_native.py',REPO/'engine/prototype/mixed_workflow.py',REPO/'engine/prototype/test_mixed_workflow.py']},
        'limits':['Readback used a completed known thread, not a hosted crash injection or ambiguous live request reconciliation.',
                  'Single-writer caller and retained external ticket/head references required; no hostile-host deletion guarantee.',
                  'Replay used constant binding callbacks; live input binding and physical I/O costs additional.',
                  'No new capability, token saving, median or Codex-app interception claim.']}
    save(root/'RESULT.json',report)
    print(json.dumps({'native_calls':0,'wire_replays':len(rows),'readback':report['persisted_thread_readback'],'seconds':report['seconds']}))


if __name__=='__main__':run(sys.argv[1])
