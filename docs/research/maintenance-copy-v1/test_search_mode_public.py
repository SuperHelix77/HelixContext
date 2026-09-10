import pytest
from evidence import Store
from workflow_memory import Memory


def populated(tmp_path):
    m = Memory(Store(tmp_path))
    for identity, body in [('one', b'alpha'), ('two', b'beta'), ('both', b'alpha beta')]:
        m.record('p', 'session', identity, body)
    m.record('other', 'session', 'secret', b'alpha beta')
    return m


def test_default_all_and_explicit_all(tmp_path):
    m = populated(tmp_path)
    assert [r['event_id'] for r in m.search('p', 'alpha beta')] == ['both']
    assert m.search('p', 'alpha beta') == m.search('p', 'alpha beta', match_mode='all')


def test_any_order_limit_and_project_isolation(tmp_path):
    m = populated(tmp_path)
    assert [r['event_id'] for r in m.search('p', 'alpha beta', match_mode='any')] == ['both', 'two', 'one']
    assert [r['event_id'] for r in m.search('p', 'alpha beta', 2, 'any')] == ['both', 'two']


@pytest.mark.parametrize('mode', [None, True, [], {}, '', 'ANY'])
def test_mode_validated_even_for_empty_query(tmp_path, mode):
    with pytest.raises(ValueError):
        populated(tmp_path).search('p', '', match_mode=mode)


def test_corruption_remains_an_error_in_any_mode(tmp_path):
    m = populated(tmp_path)
    with m.db() as db:
        db.execute("UPDATE search SET body='missing'")
    with pytest.raises(ValueError, match='index'):
        m.search('p', 'alpha beta', match_mode='any')
