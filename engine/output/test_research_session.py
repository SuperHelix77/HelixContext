"""Offline protocol tests with scripted RPC; these are NOT native usage receipts."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
import research_session as rs


def usage_event(turn,i,o,c=0,r=0):
    return {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':turn,'tokenUsage':{'total':{'inputTokens':i,'outputTokens':o,'cachedInputTokens':c,'reasoningOutputTokens':r,'totalTokens':i+o}}}}

class ScriptedRPC:
    scripts=[]
    instances=[]
    def __init__(self,cwd,out,model):
        self.out=out;self.events=[];self.calls=[];self.p=SimpleNamespace(pid=0);self.closed=False;self.index=0
        (out/'native-events.jsonl').write_bytes(b'');self.instances.append(self)
    def send(self,p):pass
    def call(self,method,params):
        self.calls.append((method,params))
        if method=='initialize':return {}
        if method=='thread/start':return {'model':'gpt-6-astra','reasoningEffort':'high','approvalPolicy':'never','thread':{'id':'thread'}}
        if method=='turn/start':
            tid='t'+str(self.index+1);script=self.scripts[self.index];self.index+=1
            events=script(tid);self.events.extend(events)
            with (self.out/'native-events.jsonl').open('a') as f:
                for e in events:f.write(json.dumps(e)+'\n')
            return {'turn':{'id':tid}}
        raise AssertionError(method)
    def read(self):raise AssertionError('Unexpected wait; scripted events exhausted')
    def close(self):self.closed=True


def completed(tid,total=(100,20),status='completed',answer=None):
    return [usage_event(tid,*total),{'method':'item/completed','params':{'threadId':'thread','turnId':tid,'item':{'type':'agentMessage','phase':'final_answer','text':answer or tid}}},{'method':'turn/completed','params':{'threadId':'thread','turn':{'id':tid,'status':status}}}]


def make(monkeypatch,tmp_path,scripts):
    ScriptedRPC.scripts=scripts;monkeypatch.setattr(rs,'RPC',ScriptedRPC)
    return rs.Session('gpt-6-astra',tmp_path,tmp_path/'out')


def test_same_thread_tool_output_and_nonduplicated_cumulative_usage(monkeypatch,tmp_path):
    with make(monkeypatch,tmp_path,[lambda t:completed(t,(100,20)),lambda t:completed(t,(250,35))]) as s:
        a,r1=s.turn('initial task');b,r2=s.turn(tool_output={'name':'helix_execution','output':'Actual check failed'})
        assert a=='t1' and b=='t2' and r1['usage_delta']['input_tokens']==100
        assert r2['usage_delta']['input_tokens']==150 and r2['usage_delta']['output_tokens']==15
        assert s.total['input_tokens']==250
        calls=s.rpc.calls;assert len([c for c in calls if c[0]=='thread/start'])==1
        turns=[p for m,p in calls if m=='turn/start'];assert all(p['threadId']=='thread' for p in turns)
        assert turns[1]['input']==[] and 'toolOutput' in turns[1]
    assert s.rpc.closed
    assert json.loads((tmp_path/'out/status.json').read_text())['usage']['input_tokens']==250


@pytest.mark.parametrize('bad',['missing','regression','stale'])
def test_bad_accounting_stops_and_prevents_retry(monkeypatch,tmp_path,bad):
    def second(t):
        es=completed(t,(150,30))
        if bad=='missing':es=es[1:]
        elif bad=='regression':es[0]=usage_event(t,90,30)
        else:es[0]=usage_event('t1',150,30)
        return es
    with make(monkeypatch,tmp_path,[lambda t:completed(t),second]) as s:
        s.turn('first')
        with pytest.raises(ValueError):s.turn(tool_output={'name':'execution','output':'delta'})
        with pytest.raises(ValueError):s.turn('retry')
        assert s.failed


def test_failed_turn_retains_partial_cost(monkeypatch,tmp_path):
    with make(monkeypatch,tmp_path,[lambda t:completed(t,(100,20)),lambda t:completed(t,(180,40),status='failed')]) as s:
        s.turn('first')
        with pytest.raises(RuntimeError):s.turn('changed state')
        assert s.total['input_tokens']==180 and s.turns[-1]['usage_delta']['input_tokens']==80


def test_duplicate_counter_is_not_double_counted(monkeypatch,tmp_path):
    def script(t):
        es=completed(t);return [es[0],*es]
    with make(monkeypatch,tmp_path,[script]) as s:
        _,r=s.turn('task');assert r['usage_delta']['input_tokens']==100


def test_previous_turn_answer_cannot_be_returned(monkeypatch,tmp_path):
    def second(t):
        old={'method':'item/completed','params':{'threadId':'thread','turnId':'t1','item':{'type':'agentMessage','phase':'final_answer','text':'stale'}}}
        return completed(t,(200,40))+[old]
    with make(monkeypatch,tmp_path,[lambda t:completed(t),second]) as s:
        s.turn('first');answer,_=s.turn('second');assert answer=='t2'
