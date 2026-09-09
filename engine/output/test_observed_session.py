import json
from types import SimpleNamespace
import observed_session


class FakeRPC:
    def __init__(self,cwd,out,model):
        self.out=out;self.p=SimpleNamespace(pid=123);self.model=model
        (out/'native-events.jsonl').write_bytes(b'')
        self.rollout=out/'source.jsonl'
        self.rollout.write_text(json.dumps({'type':'session_meta','payload':{'id':'test-thread'}})+'\n')
    def send(self,value):pass
    def close(self):pass
    def call(self,method,params):
        if method=='initialize':return {}
        assert method=='thread/start' and params['ephemeral'] is False
        return {'model':self.model,'reasoningEffort':'high','approvalPolicy':'never','thread':{'id':'test-thread','path':str(self.rollout)}}


def test_observed_session_captures_raw_without_extra_inference(tmp_path,monkeypatch):
    monkeypatch.setattr(observed_session,'RPC',FakeRPC);monkeypatch.setenv('CODEX_HOME',str(tmp_path))
    (tmp_path/'config.toml').write_text('model="synthetic"\n')
    with observed_session.Session('synthetic',tmp_path,tmp_path/'receipt') as s:
        assert s.turns==[]
    status=json.loads((tmp_path/'receipt/status.json').read_text())
    assert status['state']=='closed' and status['raw_capture']['thread_id']=='test-thread'
    assert status['raw_capture']['calls']==0


def test_config_drift_disqualifies_receipt(tmp_path,monkeypatch):
    monkeypatch.setattr(observed_session,'RPC',FakeRPC);monkeypatch.setenv('CODEX_HOME',str(tmp_path))
    config=tmp_path/'config.toml';config.write_text('model="synthetic"\n')
    with observed_session.Session('synthetic',tmp_path,tmp_path/'receipt'):
        config.write_text('model="changed"\n')
    status=json.loads((tmp_path/'receipt/status.json').read_text())
    assert status['state']=='failed'
    assert 'Configuration changed' in status['raw_capture']['error']
