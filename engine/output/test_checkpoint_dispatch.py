import copy
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'prototype'))
from evidence import Store
from workflow_memory import Memory,encode
from completion_ledger import CompletionLedger,EMPTY
from mixed_workflow import MixedWorkflow
import checkpoint_dispatch as d

PARAMS={'threadId':'thread','model':'gpt-6-astra','effort':'high','input':[{'type':'text','text':'Answer this semantic question. Ω\t  '} ]}
RAW=encode({'turn':1,'event_id':'E01','data':{},'request':'Answer this semantic question.'})
B='b'*64


def setup(tmp_path,**overrides):
    flow_store=Store(tmp_path/'evidence');state=flow_store.put(b'{"open_questions":["boundary"]}')
    flow=MixedWorkflow(CompletionLedger(Memory(flow_store)),'test','a'*64,state)
    journal=d.Journal(tmp_path/'dispatch')
    kwargs={'workflow':flow.scope,'event_id':'E01','event_bytes':RAW,'pre_head':EMPTY,
            'pre_state':state,'expected_request':copy.deepcopy(PARAMS),'expected_rpc_id':7,'binding':B}
    kwargs.update(overrides);reference=journal.prepare(**kwargs)
    return flow,journal,reference,kwargs


def wire():return {'id':7,'method':'turn/start','params':copy.deepcopy(PARAMS)}


def captured(text='Normal model answer. Ω\t  \n',*,rid=7,turn='T1',status='completed'):
    rows=[{'id':rid,'result':{'turn':{'id':turn,'status':'inProgress'}}},
          {'method':'item/completed','params':{'threadId':'thread','turnId':turn,'item':{'id':'final','type':'agentMessage','phase':'final_answer','text':text}}},
          {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':turn,'status':status}}}]
    return b'\n'.join(encode(x) for x in rows)+b'\n'


def test_durable_exact_request_before_transport_and_no_repeat(tmp_path,monkeypatch):
    flow,j,ref,_=setup(tmp_path);before=wire();observed=[];fsyncs=[]
    original=d.os.fsync
    def sync(fd):fsyncs.append(fd);return original(fd)
    monkeypatch.setattr(d.os,'fsync',sync)
    def transport(value):
        assert len(fsyncs)>=2
        marker=json.loads((j.root/ref['key']/'dispatch.json').read_bytes())
        assert marker['wire']==value==before
        observed.append(copy.deepcopy(value))
    j.send_once(ref,before,transport,current_binding=lambda:B)
    assert before==wire() and observed==[wire()]
    restarted=d.Journal(j.root)
    with pytest.raises(FileExistsError):restarted.send_once(ref,wire(),transport,current_binding=lambda:B)
    assert len(observed)==1


@pytest.mark.parametrize('failure',['before_write','after_write'])
def test_unknown_transport_outcome_never_resends(tmp_path,failure):
    _,j,ref,_=setup(tmp_path);calls=[]
    def transport(value):calls.append(value);raise OSError(failure)
    with pytest.raises(OSError):j.send_once(ref,wire(),transport,current_binding=lambda:B)
    with pytest.raises(FileExistsError):d.Journal(j.root).send_once(ref,wire(),transport,current_binding=lambda:B)
    assert len(calls)==1


def test_partial_marker_and_fsync_failure_do_not_call_transport(tmp_path,monkeypatch):
    _,j,ref,_=setup(tmp_path);calls=[]
    def fail(_):raise OSError('fsync failed')
    monkeypatch.setattr(d.os,'fsync',fail)
    with pytest.raises(OSError):j.send_once(ref,wire(),calls.append,current_binding=lambda:B)
    with pytest.raises(FileExistsError):j.send_once(ref,wire(),calls.append,current_binding=lambda:B)
    assert not calls


@pytest.mark.parametrize('change',['prompt','rpc_id','effort','model'])
def test_wrong_request_is_rejected_before_marker(tmp_path,change):
    _,j,ref,_=setup(tmp_path);w=wire()
    if change=='prompt':w['params']['input'][0]['text']='different semantic task'
    elif change=='rpc_id':w['id']=8
    else:w['params'][change]='other'
    with pytest.raises(ValueError):j.send_once(ref,w,lambda _:pytest.fail('sent'),current_binding=lambda:B)
    assert not (j.root/ref['key']/'dispatch.json').exists()


def test_conflicting_prepare_tampered_ticket_and_stale_state(tmp_path):
    _,j,ref,kw=setup(tmp_path)
    assert j.prepare(**kw)==ref
    with pytest.raises(ValueError):j.prepare(**{**kw,'event_id':'E02'})
    with pytest.raises(ValueError):j.prepare(**{**kw,'binding':'c'*64})
    with pytest.raises(ValueError):j.send_once(ref,wire(),lambda _:pytest.fail('sent'),current_binding=lambda:'c'*64)
    (j.root/ref['key']/'ticket.json').write_bytes(b'changed')
    with pytest.raises(ValueError):j.ticket(ref)


def test_exact_captured_final_commits_once_after_restart(tmp_path):
    flow,j,ref,_=setup(tmp_path);calls=[];j.send_once(ref,wire(),calls.append,current_binding=lambda:B)
    j=d.Journal(j.root);raw=captured();r=d.commit_capture(flow,j,ref,raw,after_state=flow.initial_state,current_binding=lambda:B)
    assert r['answer']=='Normal model answer. Ω\t  \n'.encode()
    replay=d.commit_capture(flow,j,ref,raw,after_state=flow.initial_state,current_binding=lambda:B)
    assert replay['replayed'] and replay['head']==r['head'] and len(calls)==1
    assert flow.recover(r['head'])[0]['answer_bytes']==r['answer']
    tail=encode({'method':'later/unrelated','params':{}})+b'\n'
    grown=d.commit_capture(flow,j,ref,raw+tail,after_state=flow.initial_state,current_binding=lambda:B)
    assert grown['replayed'] and grown['answer']==r['answer'] and len(calls)==1


def test_acceptance_without_completion_does_not_freeze_partial_capture(tmp_path):
    flow,j,ref,_=setup(tmp_path);j.send_once(ref,wire(),lambda _:None,current_binding=lambda:B)
    partial=captured().splitlines(keepends=True)[0]
    with pytest.raises(ValueError,match='not completed'):j.bind_capture(ref,partial)
    assert not (j.root/ref['key']/'capture.json').exists()
    final=d.commit_capture(flow,j,ref,captured(),after_state=flow.initial_state,current_binding=lambda:B)
    assert final['answer_owner']=='model'


def test_concurrent_senders_only_one_transport_call(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    _,j,ref,_=setup(tmp_path);calls=[]
    def send(_):
        try:j.send_once(ref,wire(),calls.append,current_binding=lambda:B);return 'sent'
        except FileExistsError:return 'held'
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(send,range(2)))
    assert sorted(results)==['held','sent'] and len(calls)==1


@pytest.mark.parametrize('change',['wrong_response_id','failed_turn','changed_wire_id','other_scope'])
def test_capture_or_scope_mismatch_cannot_commit(tmp_path,change):
    flow,j,ref,_=setup(tmp_path);j.send_once(ref,wire(),lambda _:None,current_binding=lambda:B)
    raw=captured(rid=8) if change=='wrong_response_id' else captured(status='failed') if change=='failed_turn' else captured()
    if change=='changed_wire_id':
        path=j.root/ref['key']/'dispatch.json';v=json.loads(path.read_bytes());v['wire']['id']=8;path.write_bytes(encode(v))
    if change=='other_scope':flow=MixedWorkflow(flow.ledger,'other','a'*64,flow.initial_state)
    with pytest.raises(ValueError):d.commit_capture(flow,j,ref,raw,after_state=flow.initial_state,current_binding=lambda:B)
    assert not flow.recover(EMPTY)


def test_instance_hook_preserves_other_rpc_and_restores_on_exception(tmp_path):
    _,j,ref,_=setup(tmp_path)
    class RPC:
        def __init__(self):self.sent=[]
        def send(self,x):self.sent.append(copy.deepcopy(x))
    rpc=RPC();original=rpc.send
    with pytest.raises(RuntimeError):
        with d.BoundSend(rpc,j,ref,lambda:B):
            rpc.send({'id':6,'method':'thread/read','params':{'threadId':'thread'}})
            rpc.send(wire());raise RuntimeError('native observer failed')
    assert rpc.send==original and rpc.sent[-1]==wire() and len(rpc.sent)==2
