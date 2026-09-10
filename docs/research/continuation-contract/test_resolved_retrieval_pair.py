import copy
import hashlib
import json
import pytest
import luna_resolved_retrieval_pair as pair


@pytest.mark.parametrize('case', ['selection', 'cold'])
def test_new_fixture_matches_independent_oracle(case, tmp_path):
    spec = pair.fixtures()[case]
    raw = json.dumps(spec['source'], ensure_ascii=False).encode()
    result = pair.resolve.execute(spec['task'], raw, hashlib.sha256(raw).hexdigest())
    assert result['state'] == 'RESOLVED'
    assert pair.equal(result['answer'], pair.expected(case, spec))
    if case == 'selection':
        assert result['answer']['total_count'] == 320 and len(result['answer']['eligible']) > 2
    else:
        assert result['answer']['evidence_turn'] == 1
        assert result['answer']['label_exact'].endswith(' \t ')


def test_binding_failure_is_not_an_answer(tmp_path):
    spec = pair.fixtures()['selection']
    store = pair.Store(tmp_path)
    ref = store.put(json.dumps(spec['source']).encode())
    state = {'schema': pair.gate.VERSION, 'adapter_version': pair.resolve.VERSION,
             'task_sha256': hashlib.sha256(spec['task'].encode()).hexdigest(),
             'source_ref': ref, 'active_constraints': []}
    original = pair.gate.state_root(state)
    state['active_constraints'] = ['Also apply the current project privacy policy.']
    result = pair.gate.dispatch(spec['task'], store, ref, expected_state_root=original,
        current_state=lambda: state, semantic=lambda *_: pytest.fail('Stale state must be recovered'))
    assert result['state'] == 'HOLD_FOR_RECOVERY' and 'answer' not in result


def test_inherited_rule_keeps_semantic_execution_inside_engine(tmp_path):
    spec = pair.fixtures()['cold']
    store = pair.Store(tmp_path)
    ref = store.put(json.dumps(spec['source']).encode())
    state = {'schema': pair.gate.VERSION, 'adapter_version': pair.resolve.VERSION,
             'task_sha256': hashlib.sha256(spec['task'].encode()).hexdigest(),
             'source_ref': ref, 'active_constraints': ['Reconcile with the amended label policy.']}
    calls = []
    result = pair.gate.dispatch(spec['task'], store, ref, expected_state_root=pair.gate.state_root(state),
        current_state=lambda: copy.deepcopy(state), semantic=lambda *args: calls.append(args))
    assert result['engine_active'] and result['state'] == 'SEMANTIC_DISPATCHED' and len(calls) == 1


def test_json_type_and_exact_string_are_part_of_grade():
    assert not pair.equal({'x': True}, {'x': 1})
    assert not pair.equal({'x': '0001 '}, {'x': '1'})
