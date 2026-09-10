from tempfile import TemporaryDirectory
from evidence import Store
from workflow_memory import Memory

checks = 0
def verify(condition):
    global checks
    assert condition
    checks += 1

def ids(records):
    return [r['event_id'] for r in records]

with TemporaryDirectory(prefix='.search-review-', dir='.') as root:
    m = Memory(Store(root))
    for event, body in [('alpha', b'alpha'), ('beta', b'beta'),
                        ('operator', b'OR'), ('all', b'alpha OR beta')]:
        m.record('literal', 's', event, body)
    verify(ids(m.search('literal', '"alpha" OR (beta*)', match_mode='all')) == ['all'])
    verify(ids(m.search('literal', '"alpha" OR (beta*)', match_mode='any')) == ['all', 'operator', 'beta', 'alpha'])
    verify(ids(m.search('literal', '"OR"', match_mode='any')) == ['all', 'operator'])

    raw = 'café blue green\x00\ufffd'.encode() + b'\xff'
    ref = m.record('unicode', 's', 'phrase', raw)
    m.record('unicode', 's', 'reversed', b'green blue')
    for mode in ('all', 'any'):
        found = m.search('unicode', 'café blue_green', match_mode=mode)
        verify(ids(found) == ['phrase'])
        verify(found[0] == {**ref, 'ordinal': found[0]['ordinal']})
        verify(m.retrieve('unicode', [found[0]['record_hash']])[0]['raw'] == raw)

    m.record('integrity', 's', 'nonmatching', b'unrelated cold evidence')
    m.record('integrity', 's', 'newest', b'alpha beta')
    with m.db() as db:
        db.execute("DELETE FROM search WHERE rowid=(SELECT ordinal FROM events WHERE project='integrity' AND event_id='nonmatching')")
    for mode in ('all', 'any'):
        try:
            m.search('integrity', 'alpha beta', 1, mode)
        except ValueError as exc:
            verify(str(exc) == 'Search index does not match archived evidence; rebuild or use exact timeline recovery')
        else:
            raise AssertionError('Nonmatching corruption escaped full validation')
    verify(ids(m.search('literal', 'OR', match_mode='any')) == ['all', 'operator'])
print(f'{checks} additional semantic assertions passed: literal operators, Unicode/FTS phrase behavior, exact binary provenance, and full project-scoped corruption checks beyond the result limit.')
