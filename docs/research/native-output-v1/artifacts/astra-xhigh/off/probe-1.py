from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from evidence import Store
from workflow_memory import Memory

with TemporaryDirectory(prefix='.search-check-', dir=Path.cwd()) as tmp:
    m = Memory(Store(tmp))
    bodies = [('alpha', b'alpha'), ('beta', b'beta'), ('or', b'OR'),
              ('both', b'alpha beta'), ('literal', b'alpha OR beta'),
              ('unicode', 'café 東京'.encode()), ('split', b'foo bar'),
              ('underscore', b'foo_bar'), ('unrelated', b'untouched')]
    refs = {key: m.record('p', 's', key, body) for key, body in bodies}
    m.record('other', 's', 'foreign', b'alpha OR beta')
    ids = lambda query, mode: [r['event_id'] for r in m.search('p', query, match_mode=mode)]
    assert ids('alpha OR beta', 'all') == ['literal']
    assert ids('alpha OR beta', 'any') == ['literal', 'both', 'or', 'beta', 'alpha']
    assert ids('alpha NOT beta', 'all') == []
    assert ids('alpha NOT beta', 'any') == ['literal', 'both', 'beta', 'alpha']
    assert ids('"alpha"* -beta', 'all') == ['literal', 'both']
    assert ids('body:alpha', 'all') == []
    assert ids('body:alpha', 'any') == ['literal', 'both', 'alpha']
    assert ids('CAFÉ 東京', 'all') == ['unicode']
    assert ids('absent 東京', 'any') == ['unicode']
    assert ids('foo_bar', 'all') == ids('foo_bar', 'any') == ['underscore', 'split']
    for mode in ('all', 'any'):
        for query in ('', '  ', '"*+-():'):
            assert m.search('p', query, match_mode=mode) == []
        for query in ('', 'alpha'):
            for kwargs in ({'project': ''}, {'project': None}, {'query': None},
                           {'limit': True}, {'limit': 0}, {'limit': 101}, {'limit': 1.5}):
                request = dict(project='p', query=query, match_mode=mode)
                request.update(kwargs)
                with pytest.raises(ValueError):
                    m.search(**request)
        for row in m.search('p', 'alpha beta', 100, mode):
            assert {k: v for k, v in row.items() if k != 'ordinal'} == refs[row['event_id']]
        for mode_invalid in (None, True, 1, b'all', [], {}, '', 'ALL', 'any ', 'or'):
            for query in ('', 'alpha'):
                with pytest.raises(ValueError):
                    m.search('p', query, match_mode=mode_invalid)
    with m.db() as db:
        db.execute("DELETE FROM search WHERE rowid=(SELECT ordinal FROM events WHERE project='p' AND event_id='unrelated')")
    for mode in ('all', 'any'):
        for query in ('alpha beta', 'no_match_here'):
            with pytest.raises(ValueError, match='index'):
                m.search('p', query, 1, mode)
    m.rebuild_index('p')
    source = m.store.root / 'objects' / refs['unrelated']['source_hash']
    source.write_bytes(b'tampered')
    for mode in ('all', 'any'):
        with pytest.raises(ValueError, match='hash mismatch'):
            m.search('p', 'alpha beta', 1, mode)
print('Supplemental checks passed: literal operators, Unicode, existing FTS tokenization, validation, exact references, and full-project corruption detection in both modes.')
