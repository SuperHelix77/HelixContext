import copy
import hashlib
import json
from pathlib import Path
import pytest
import bound_retrieval as gate
import resolved_retrieval
from evidence import Store


def fixture(tmp_path):
    path = Path(__file__).resolve().parents[2] / 'benchmarks/frozen-high/protocol/reasoning-v2.json'
    spec = json.loads(path.read_text())
    store = Store(tmp_path / 'store')
    ref = store.put(json.dumps(spec['records']).encode())
    task = spec['task']
    state = {'schema': gate.VERSION, 'adapter_version': resolved_retrieval.VERSION,
             'task_sha256': hashlib.sha256(task.encode()).hexdigest(),
             'source_ref': ref, 'active_constraints': []}
    return task, store, ref, state


def test_closed_request_and_inherited_authority(tmp_path):
    task, store, ref, state = fixture(tmp_path)
    root = gate.state_root(state)
    result = gate.dispatch(task, store, ref, expected_state_root=root,
                           current_state=lambda: state, semantic=lambda *_: pytest.fail('extra inference'))
    assert result['state'] == 'RESOLVED' and result['model_calls'] == 0
    assert result['state_root'] == root and result['unchecked_obligations']
    state['active_constraints'] = ['Do not disclose rows that are restricted by the project contract.']
    calls = []
    result = gate.dispatch(task, store, ref, expected_state_root=gate.state_root(state),
                           current_state=lambda: state, semantic=lambda *a: calls.append(a))
    assert result['state'] == 'SEMANTIC_DISPATCHED' and calls == [(task, ref)]


@pytest.mark.parametrize('change', ['task', 'source', 'version', 'mutated_state', 'missing_root', 'missing_constraints'])
def test_binding_faults_hold_without_inference(tmp_path, change):
    task, store, ref, state = fixture(tmp_path)
    root = gate.state_root(state)
    if change == 'task': task += ' changed'
    if change == 'source': ref = {**ref, 'sha256': '0' * 64}
    if change == 'version': state['adapter_version'] = 'future'
    if change == 'mutated_state': state['active_constraints'] = ['Earlier constraint']
    if change == 'missing_root': root = None
    if change == 'missing_constraints':
        del state['active_constraints']
        root = gate.state_root(state)
    result = gate.dispatch(task, store, ref, expected_state_root=root,
                           current_state=lambda: state, semantic=lambda *_: pytest.fail('unsafe inference'))
    assert result['state'] == 'HOLD_FOR_RECOVERY' and 'answer' not in result


def test_state_change_during_read_withholds_answer(tmp_path):
    task, store, ref, state = fixture(tmp_path)
    root = gate.state_root(state)
    get = store.get
    def read_then_change(key):
        raw = get(key)
        state['active_constraints'] = ['A new requirement arrived.']
        return raw
    store.get = read_then_change
    result = gate.dispatch(task, store, ref, expected_state_root=root,
                           current_state=lambda: state, semantic=lambda *_: pytest.fail('new state not yet bound'))
    assert result['state'] == 'HOLD_FOR_RECOVERY' and 'answer' not in result


def test_unknown_request_and_schema_keep_semantic_path(tmp_path):
    task, store, ref, state = fixture(tmp_path)
    task += ' Also explain exceptions.'
    state['task_sha256'] = hashlib.sha256(task.encode()).hexdigest()
    calls = []
    result = gate.dispatch(task, store, ref, expected_state_root=gate.state_root(state),
                           current_state=lambda: copy.deepcopy(state), semantic=lambda *a: calls.append(a))
    assert result['state'] == 'SEMANTIC_DISPATCHED' and len(calls) == 1


def test_oversized_integer_declines_without_disabling_engine(tmp_path):
    task, store, ref, state = fixture(tmp_path)
    task = task.replace('at least 2.', 'at least ' + '9' * 5000 + '.')
    state['task_sha256'] = hashlib.sha256(task.encode()).hexdigest()
    calls = []
    result = gate.dispatch(task, store, ref, expected_state_root=gate.state_root(state),
                           current_state=lambda: state, semantic=lambda *a: calls.append(a))
    assert result['engine_active'] and result['state'] == 'SEMANTIC_DISPATCHED' and len(calls) == 1
