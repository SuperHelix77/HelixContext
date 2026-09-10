from pathlib import Path
from tempfile import TemporaryDirectory
from evidence import Store
from workflow_memory import Memory

with TemporaryDirectory(dir='.') as directory:
    m = Memory(Store(Path(directory)))
    refs = {}
    for event, raw in [('alpha', b'alpha'), ('beta', b'beta'), ('operator', b'OR'), ('both', b'alpha beta'), ('unicode', 'café 東京'.encode())]:
        refs[event] = m.record('p', 's', event, raw)
    ids = lambda query, mode: [r['event_id'] for r in m.search('p', query, match_mode=mode)]
    assert ids('alpha OR beta', 'all') == []
    assert ids('alpha OR beta', 'any') == ['both', 'operator', 'beta', 'alpha']
    assert ids('"alpha" -beta*', 'all') == ['both']
    assert ids('"alpha" -beta*', 'any') == ['both', 'beta', 'alpha']
    for mode in ('all', 'any'):
        assert ids('café 東京', mode) == ['unicode']
        assert m.search('p', '!!!', match_mode=mode) == []
        result = m.search('p', 'alpha', 1, mode)[0]
        assert {k: result[k] for k in refs['both']} == refs['both']
        for project, query, limit in [('', '', 1), ('p', None, 1), ('p', '', True), ('p', '', 0), ('p', '', 101)]:
            try:
                m.search(project, query, limit, mode)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid arguments accepted')
    with m.db() as db:
        db.execute("UPDATE search SET body='tampered' WHERE rowid=(SELECT ordinal FROM events WHERE event_id='unicode')")
    for mode in ('all', 'any'):
        try:
            m.search('p', 'alpha', 1, mode)
        except ValueError as error:
            assert 'index' in str(error)
        else:
            raise AssertionError('Nonmatching corruption bypassed')
print('Supplemental checks passed: literal operators, Unicode, empty queries, validation, exact references, and nonmatching corruption with limit=1.')
