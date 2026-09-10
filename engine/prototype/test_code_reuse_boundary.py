"""Offline composition checks. No model calls or semantic sufficiency claims."""
import hashlib
import json

import pytest

from copy_handles import assemble, freeze
from evidence import Store
from semantic_execution import Step, execute_decision


def setup_case(tmp_path):
    source = b'def calculate(x):\n    return x + 1\n'
    store = Store(tmp_path / 'evidence')
    key = store.put(source)['sha256']
    reference, _ = freeze(store, {'existing': {
        'source_sha256': key, 'start_byte': 0, 'end_byte': len(source)}})
    # The caller supplies the complete declared world for this synthetic test.
    # This is not a discovery algorithm for arbitrary repository dependencies.
    world = {'source': key, 'request': 'increment by one',
             'dependency': 'integer-domain-v1', 'epoch': 0}
    def binding():
        return hashlib.sha256(json.dumps(world, sort_keys=True).encode()).hexdigest()
    artifact, _ = assemble(store, reference, ['existing'])
    decision = {'artifact': artifact, 'assessment': 'Use the existing implementation for this bound request.',
                'semantic_obligations': []}
    return world, binding, binding(), decision


@pytest.mark.parametrize('field,value', [('source', 'different'),
    ('request', 'increment by two'), ('dependency', 'different'), ('epoch', 1)])
def test_changed_world_never_reuses_accepted_decision(tmp_path, field, value):
    world, binding, expected, decision = setup_case(tmp_path)
    world[field] = value
    result = execute_decision(decision, expected_binding=expected, current_binding=binding,
        steps=(Step('publish', lambda _: pytest.fail('Stale decision executed')),))
    assert result['state'] == 'HOLD'
    assert result['model_calls_added'] == 0 and result['engine_active']


def test_correct_hash_wrong_semantics_does_not_become_success(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    # The independent caller check is intentionally stronger than hash equality.
    # It is a finite semantic counterexample, not a general semantic oracle.
    decision['artifact'] = b'def calculate(x):\n    return x - 1\n'
    def check(raw):
        scope = {}
        exec(compile(raw, '<trusted local test fixture>', 'exec'), scope)
        return {'passed': scope['calculate'](3) == 4}
    result = execute_decision(decision, expected_binding=expected, current_binding=binding,
        steps=(Step('check', check), Step('publish', lambda _: pytest.fail('Wrong code published'))))
    assert result['state'] == 'SEMANTIC_REENTRY'


def test_final_step_authority_change_is_not_success(tmp_path):
    world, binding, expected, decision = setup_case(tmp_path)
    effects = []
    def publish(raw):
        effects.append(raw)
        world['request'] = 'increment by two'
        return {'passed': True, 'artifact_bytes': len(raw)}
    result = execute_decision(decision, expected_binding=expected, current_binding=binding,
        steps=(Step('publish', publish),))
    assert result['state'] == 'RECONCILE'
    assert len(effects) == len(result['receipts']) == 1
    assert result['model_calls_added'] == 0


def test_binding_failure_after_effect_preserves_receipt_without_retry(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    effects = []
    def checked_binding():
        if effects:
            raise OSError('State unavailable after effect')
        return binding()
    def publish(raw):
        effects.append(raw)
        return {'passed': True}
    result = execute_decision(decision, expected_binding=expected, current_binding=checked_binding,
        steps=(Step('publish', publish),))
    assert result['state'] == 'RECONCILE'
    assert len(effects) == len(result['receipts']) == 1


def test_binding_failure_between_steps_preserves_receipt(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    effects = []
    def checked_binding():
        if effects:
            raise OSError('State unavailable between effects')
        return binding()
    def first(raw):
        effects.append(raw)
        return {'passed': True}
    result = execute_decision(decision, expected_binding=expected, current_binding=checked_binding,
        steps=(Step('first', first), Step('second', lambda _: pytest.fail('Retried after state loss'))))
    assert result['state'] == 'RECONCILE'
    assert len(effects) == len(result['receipts']) == 1


def test_interrupted_publication_is_not_replayed(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    effects = []
    def publish(raw):
        effects.append(raw)
        raise OSError('Interrupted after effect')
    result = execute_decision(decision, expected_binding=expected, current_binding=binding,
        steps=(Step('publish', publish),))
    assert result['state'] == 'RECONCILE'
    assert len(effects) == len(result['receipts']) == 1


def test_unchanged_bound_code_completes_without_inference(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    effects = []
    def publish(raw):
        effects.append(raw)
        return {'passed': True}
    result = execute_decision(decision, expected_binding=expected, current_binding=binding,
        steps=(Step('publish', publish),))
    assert result['state'] == 'MECHANICS_COMPLETED'
    assert effects == [decision['artifact']]
    assert result['model_calls_added'] == 0
    assert result['binding_checks'] == 2


def test_initial_unavailable_authority_never_executes(tmp_path):
    _, _, expected, decision = setup_case(tmp_path)
    def unavailable():
        raise OSError('Authority unavailable before work')
    result = execute_decision(decision, expected_binding=expected, current_binding=unavailable,
        steps=(Step('publish', lambda _: pytest.fail('Executed without authority')),))
    assert result['state'] == 'HOLD' and result['receipts'] == []


def test_closing_check_does_not_add_a_full_world_read(tmp_path):
    _, binding, expected, decision = setup_case(tmp_path)
    calls = []
    def counted():
        calls.append('binding')
        return binding()
    result = execute_decision(decision, expected_binding=expected, current_binding=counted,
        steps=tuple(Step(str(i), lambda _: {'passed': True}) for i in range(5)))
    assert result['state'] == 'MECHANICS_COMPLETED'
    assert result['binding_checks'] == len(calls) == 6
    assert result['binding_seconds'] >= 0
