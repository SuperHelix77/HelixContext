from tempfile import TemporaryDirectory
from evidence import Store
from before import Memory as BeforeMemory
from workflow_memory import Memory

with TemporaryDirectory(prefix='memory-api-review-', dir='/private/tmp') as root:
    store = Store(root)
    before = BeforeMemory(store)
    current = Memory(store)
    for n in range(12):
        current.record('p', 's', str(n), b'alpha beta')
    original = before.search('p', 'alpha beta')
    proposed = current.search('p', 'alpha beta')
    explicit = current.search('p', 'alpha beta', 10)
    assert explicit == original
    assert current.search('p', 'alpha beta', 10, 'all') == original
    assert current.search('p', 'alpha beta', 10, 'any') == original
    print('Explicit limit=10 matches before.py exactly in both modes.', flush=True)
    for label, rows in [('before default', original), ('proposed default', proposed),
                        ('proposed any default', current.search('p', 'alpha beta', match_mode='any'))]:
        print(f'{label}: count={len(rows)}, event_ids={[r["event_id"] for r in rows]}', flush=True)
    assert proposed == original, 'Existing two-argument search lost the tenth result: default limit changed from 10 to 9'
