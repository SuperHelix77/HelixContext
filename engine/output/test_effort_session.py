"""Exercise explicit effort and mismatch failure without a model/server call."""
import json
from pathlib import Path
import pytest
import effort_session as m


class FakeRPC:
    def __init__(self, cwd, out, model):
        self.out = out; self.events = []; self.p = type('P', (), {'pid': 0})()
        (out / 'native-events.jsonl').write_text('')
        (out / 'requests.jsonl').write_text('')
    def send(self, value): pass
    def close(self): pass
    def call(self, method, params):
        with (self.out / 'requests.jsonl').open('a') as f:
            f.write(json.dumps({'method': method, 'params': params})+'\n')
        if method == 'initialize': return {}
        if method == 'thread/start':
            return {'thread': {'id': 'fake-thread', 'path': None}, 'model': params['model'],
                    'reasoningEffort': params['config']['model_reasoning_effort'], 'approvalPolicy': 'never'}
        if method == 'turn/start':
            counts = dict(inputTokens=10, cachedInputTokens=0, outputTokens=2, reasoningOutputTokens=1, totalTokens=12)
            self.events += [
                {'method': 'thread/tokenUsage/updated', 'params': {'threadId': 'fake-thread', 'turnId': 't', 'tokenUsage': {'total': counts, 'last': counts}}},
                {'method': 'item/completed', 'params': {'threadId': 'fake-thread', 'turnId': 't', 'item': {'type': 'agentMessage', 'phase': 'final_answer', 'text': 'answer'}}},
                {'method': 'turn/completed', 'params': {'threadId': 'fake-thread', 'turn': {'id': 't', 'status': 'completed'}}}]
            return {'turn': {'id': 't'}}
        raise AssertionError(method)


@pytest.mark.parametrize('effort', ['high', 'xhigh'])
def test_effort_attached_to_every_native_turn(tmp_path, monkeypatch, effort):
    monkeypatch.setattr(m, 'RPC', FakeRPC)
    monkeypatch.setattr(m, 'capture', lambda *args: {'captured': True})
    with m.Session('gpt-6-astra', tmp_path, tmp_path / 'out', effort=effort) as s:
        s.rollout_path = 'fake'
        answer, _ = s.turn('task')
        assert answer == 'answer'
    status = json.loads((tmp_path / 'out/status.json').read_text())
    assert not s.failed and status['effort'] == effort
    assert status['effective_config_binding']['effort'] == effort
    requests = [json.loads(x) for x in (tmp_path / 'out/requests.jsonl').read_text().splitlines()]
    assert next(x for x in requests if x['method'] == 'thread/start')['params']['config']['model_reasoning_effort'] == effort
    assert next(x for x in requests if x['method'] == 'turn/start')['params']['effort'] == effort


def test_native_mismatch_stops_before_inference(tmp_path, monkeypatch):
    class Wrong(FakeRPC):
        def call(self, method, params):
            reply = super().call(method, params)
            if method == 'thread/start': reply['reasoningEffort'] = 'high'
            return reply
    monkeypatch.setattr(m, 'RPC', Wrong)
    with pytest.raises(ValueError, match='configuration mismatch'):
        m.Session('gpt-6-astra', tmp_path, tmp_path / 'out', effort='xhigh')
    requests = (tmp_path / 'out/requests.jsonl').read_text()
    assert 'turn/start' not in requests
