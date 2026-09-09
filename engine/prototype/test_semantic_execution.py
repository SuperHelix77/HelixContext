import pytest
from semantic_execution import Step,execute_decision


def decision(**changes):
    return dict(artifact=b'exact source\n',assessment='Chosen implementation; finite checks have limits.',
                semantic_obligations=[],**changes)


@pytest.mark.parametrize('model',['gpt-5.6-luna','gpt-5.6-sol','gpt-6-astra'])
def test_pending_mechanics_do_not_become_semantic_stop(model):
    calls=[]
    def run(name):
        def step(raw):
            assert raw==b'exact source\n';calls.append(name);return {'passed':True,'model_context':model}
        return Step(name,step)
    r=execute_decision(decision(),expected_binding='bound',current_binding=lambda:'bound',
                       steps=(run('tests'),run('oracle'),run('publish')))
    assert calls==['tests','oracle','publish'] and r['state']=='MECHANICS_COMPLETED'
    assert r['engine_active'] and r['model_calls_added']==0


def test_semantic_question_preserved():
    d=decision();d['semantic_obligations']=['Does this satisfy the unstated tie rule?']
    r=execute_decision(d,expected_binding='b',current_binding=lambda:'b',steps=(Step('publish',lambda x:pytest.fail('published')),))
    assert r['state']=='SEMANTIC_REENTRY'


def test_failed_check_blocks_publish():
    r=execute_decision(decision(),expected_binding='b',current_binding=lambda:'b',
      steps=(Step('test',lambda x:{'passed':False}),Step('publish',lambda x:pytest.fail('published'))))
    assert r['state']=='SEMANTIC_REENTRY' and len(r['receipts'])==1


def test_change_between_steps_holds():
    binding=['b']
    def first(raw):binding[0]='changed';return {'passed':True}
    r=execute_decision(decision(),expected_binding='b',current_binding=lambda:binding[0],
       steps=(Step('test',first),Step('publish',lambda x:pytest.fail('published'))))
    assert r['state']=='HOLD'


def test_effect_then_error_is_not_retried():
    effects=[]
    def step(raw):effects.append(raw);raise OSError('delivery uncertain')
    r=execute_decision(decision(),expected_binding='b',current_binding=lambda:'b',steps=(Step('publish',step),))
    assert len(effects)==1 and r['state']=='RECONCILE'


def test_legacy_ambiguous_obligations_rejected():
    d=decision();d['unresolved']=['run tests']
    with pytest.raises(ValueError):execute_decision(d,expected_binding='b',current_binding=lambda:'b',steps=())
