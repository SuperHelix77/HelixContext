import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('mixed_driver_test',HERE/'driver.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


def test_delivery_is_prefix_only_and_public_checks_arrive_on_time(tmp_path):
    (tmp_path/'planner.py').write_bytes((HERE/'planner.py').read_bytes())
    delivered=[]
    for e in d.protocol.fixture()['events']:
        delivered=d.deliver(tmp_path,delivered,e)
        assert d.read(tmp_path/'history.json')==delivered
        assert max(x['turn'] for x in delivered)==e['turn']
        assert not (tmp_path/'reference.py').exists() and not (tmp_path/'checks.py').exists()
        if e['turn']<25:assert not (tmp_path/'public_checks.py').exists()
        elif e['turn']<38:assert 'label_exact' not in (tmp_path/'public_checks.py').read_text()
        elif e['turn']<50:assert 'previous exact bytes' not in (tmp_path/'public_checks.py').read_text()
        prompt=d.task_prompt(tmp_path,e,delivered,True)
        if not d.passive(e) and e['turn']<38:assert '0000000081700321' not in prompt
        if e['turn']==38:assert '0000000081700321' in prompt


def test_history_crash_never_looks_complete(tmp_path,monkeypatch):
    d.atomic(tmp_path/'history.json',b'[]')
    def fail(*args):raise OSError('interrupted publication')
    monkeypatch.setattr(d.os,'replace',fail)
    with pytest.raises(OSError):d.deliver(tmp_path,[],d.protocol.fixture()['events'][0])
    assert (tmp_path/'history.json').read_bytes()==b'[]'
    with pytest.raises(FileExistsError):d.deliver(tmp_path,[],d.protocol.fixture()['events'][0])


def test_current_request_selects_only_exact_old_evidence(tmp_path):
    events=d.protocol.fixture()['events'];(tmp_path/'planner.py').write_bytes((HERE/'planner.py').read_bytes())
    e=events[37];wrong=json.loads(json.dumps(e));wrong['data']['required_inventory_tag']='missing'
    with pytest.raises(ValueError):d.task_prompt(tmp_path,wrong,events[:38],True)
    duplicated=events[:38]+[events[0]]
    with pytest.raises(ValueError):d.task_prompt(tmp_path,e,duplicated,True)
    assert 'Caller-supplied exact' not in d.task_prompt(tmp_path,e,events[:38],False)


def test_scripted_common_driver_all_events_preserves_final_and_original_rpc(tmp_path,monkeypatch):
    # Offline lifecycle simulation only. Oracle/reference never enter the real driver.
    calls=[]
    class FakeSession:
        def __init__(self,model,cwd,out,skill,effort):
            self.model=model;self.cwd=cwd;self.out=out;out.mkdir();self.skill=skill
            self.thread='thread-'+cwd.name;self.turns=[];self.total=None;self.failed=False;self.started=d.time.perf_counter()
            self.rpc=SimpleNamespace(next_id=0,send=lambda wire: calls.append(wire))
            self.registration={'thread_id':self.thread,'skill_sha256':d.sha(skill)}
            (out/'native-events.jsonl').write_bytes(b'')
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def turn(self,task):
            e=d.read(self.cwd/'history.json')[-1];n=e['turn']
            req={'threadId':self.thread,'model':self.model,'effort':'high','input':[{'type':'text','text':task}]}
            if not self.turns:req['input'].append({'type':'skill','name':'helixcontext','path':str(self.skill)})
            self.rpc.next_id+=1;self.rpc.send({'id':self.rpc.next_id,'method':'turn/start','params':req})
            if n==12:answer='The examples disagree about adjacency. Should the default merge touching intervals? I have not changed the code.'
            elif n in [25,38,50]:
                (self.cwd/'planner.py').write_bytes((HERE/'reference.py').read_bytes())
                if n>=38:d.save(self.cwd/'plan.json',d.checks.expected_plan())
                answer=f'Completed checkpoint {n}. Verification passed. Ordinary full answer.'
            else:answer='ACK '+e['event_id']
            tid='turn-'+str(n)
            events=[{'id':self.rpc.next_id,'result':{'turn':{'id':tid}}},
                    {'method':'item/completed','params':{'threadId':self.thread,'turnId':tid,'item':{'type':'agentMessage','phase':'final_answer','id':'a'+str(n),'text':answer}}},
                    {'method':'turn/completed','params':{'threadId':self.thread,'turn':{'id':tid,'status':'completed'}}}]
            with (self.out/'native-events.jsonl').open('ab') as f:
                for x in events:f.write(d.encode(x)+b'\n')
            self.total={'input_tokens':100*(len(self.turns)+1),'output_tokens':10*(len(self.turns)+1)}
            row={'turn_id':tid,'usage_delta':{'input_tokens':100,'output_tokens':10}}
            self.turns.append(row);return answer,row
    root=tmp_path/'run'
    monkeypatch.setattr(d,'Session',FakeSession)
    monkeypatch.setattr(d,'review_clarification',lambda *a:0)
    monkeypatch.setattr(d.memory,'prepare',lambda cwd,task,query,out: (out.mkdir(),(out/'receipt.json').write_text('{}')))
    monkeypatch.setattr(d.memory,'attach',lambda cwd,task,out,pin:task)
    d.prepare(root);d.preflight(root);d.run(root)
    result=d.read(root/'results.json');assert result['state']=='AWAITING_FINAL_SEMANTIC_AUDIT'
    assert len(calls)==54
    for row in result['rows']:
        assert len(row['completed_events'])==50 and row['restart']=='PASS'
        assert sum(x['model_invoked'] for x in row['completed_events'])==(50 if row['arm']=='off' else 4)
        for x in row['completed_events']:
            if x['event_id'] in ['E12','E25','E38','E50']:assert x['model_invoked']
    for arm in ['off','on']:
        folder=root/arm
        assert not (folder/'reference.py').exists() and not (folder/'checks.py').exists()
        assert len(d.read(folder/'answers.json'))==50
    with pytest.raises(FileExistsError):d.run(root)
