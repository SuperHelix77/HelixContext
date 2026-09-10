import tempfile
from pathlib import Path
from evidence import Store
from workflow_memory import Memory

with tempfile.TemporaryDirectory() as directory:
    memory = Memory(Store(Path(directory)))
    memory.record('p', 's', '1', b'alpha beta')
    memory.record('p', 's', '2', b'alpha')
    memory.record('p', 's', '3', b'OR beta')
    assert [r['event_id'] for r in memory.search('p', 'alpha beta')] == ['1']
    assert [r['event_id'] for r in memory.search('p', 'alpha beta', match_mode='any')] == ['3', '2', '1']
    assert [r['event_id'] for r in memory.search('p', 'alpha OR beta')] == []
    assert memory.search('p', 'alpha*') == memory.search('p', 'alpha')
    for invalid in (None, True, 1, '', 'ANY'):
        try:
            memory.search('p', '', match_mode=invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f'accepted invalid mode: {invalid!r}')
print('focused search-mode checks passed')
