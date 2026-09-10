import pytest
from dynamic_tool_rpc import rpc_type


SPEC = [{'type': 'function', 'name': 'helix_probe', 'description': 'Bound read-only probe', 'inputSchema': {'type': 'object'}}]


def client(handler):
    cls = rpc_type(SPEC, handler); obj = object.__new__(cls)
    obj.bound_thread = 't'; obj.active_turn = 'u'; obj.delivered = {}
    return obj


def request(**changed):
    return {'id': 1, 'method': 'item/tool/call', 'params': {'threadId': 't', 'turnId': 'u', 'callId': 'c', 'tool': 'helix_probe', 'arguments': {}, **changed}}


def test_exact_duplicate_does_not_reexecute():
    calls = []
    c = client(lambda p: calls.append(p) or {'success': True, 'contentItems': [{'type': 'inputText', 'text': 'bound evidence'}]})
    assert c.dispatch(request()) == c.dispatch(request())
    assert len(calls) == 1
    with pytest.raises(ValueError, match='Conflicting'):
        c.dispatch(request(arguments={'different': True}))
    assert len(calls) == 1


@pytest.mark.parametrize('change', [{'threadId': 'other'}, {'turnId': 'old'}, {'tool': 'shell'}, {'namespace': 'foreign'}, {'callId': ''}])
def test_unbound_request_cannot_execute(change):
    c = client(lambda p: pytest.fail('Unbound handler executed'))
    with pytest.raises(ValueError): c.dispatch(request(**change))


def test_permission_request_is_not_autoapproved():
    c = client(lambda p: pytest.fail('Permission request reached handler'))
    e = request(); e['method'] = 'item/permissions/requestApproval'
    with pytest.raises(ValueError): c.dispatch(e)


def test_bad_response_stops():
    c = client(lambda p: {'success': 'yes', 'contentItems': []})
    with pytest.raises(ValueError, match='response'): c.dispatch(request())
