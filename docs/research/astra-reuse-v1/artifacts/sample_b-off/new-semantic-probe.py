import inspect
from tempfile import TemporaryDirectory
from pathlib import Path
from evidence import Store
from before import Memory as Baseline
from workflow_memory import Memory as Proposed

print('baseline signature:', inspect.signature(Baseline.search))
print('proposed signature:', inspect.signature(Proposed.search))
with TemporaryDirectory(prefix='search-default-review-') as tmp:
    for name, cls in [('baseline', Baseline), ('proposed', Proposed)]:
        memory = cls(Store(Path(tmp) / name))
        for i in range(12):
            memory.record('p', 's', str(i), b'alpha beta')
        default = memory.search('p', 'alpha beta')
        explicit = memory.search('p', 'alpha beta', 10)
        print(name, 'omitted limit:', len(default), [r['event_id'] for r in default])
        print(name, 'explicit limit=10:', len(explicit), [r['event_id'] for r in explicit])
        assert len(explicit) == 10
        if name == 'baseline':
            assert len(default) == 10
        else:
            assert len(default) == 9
            for mode in ('all', 'any'):
                assert len(memory.search('p', 'alpha beta', match_mode=mode)) == 9
                print(name, mode, 'omitted limit:', len(memory.search('p', 'alpha beta', match_mode=mode)))
print('Confirmed: unchanged two-argument calls lose the tenth result; explicit limits still work.')
