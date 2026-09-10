"""Independent finite search-mode checks; never supplied in model workspaces."""
import itertools
from pathlib import Path
import re
import sys
import tempfile


def check(cwd):
    sys.path.insert(0, str(Path(cwd).resolve()))
    from evidence import Store
    from workflow_memory import Memory
    checked = 0
    with tempfile.TemporaryDirectory(prefix='helix-maintenance-oracle-') as folder:
        m = Memory(Store(Path(folder) / 'normal'))
        documents = []
        words = ('alpha', 'beta', 'gamma', 'or')
        for index, bits in enumerate(itertools.product((False, True), repeat=len(words))):
            tokens = {w for w, present in zip(words, bits) if present}
            raw = (' '.join(sorted(tokens)) or 'unrelated').encode()
            ref = m.record('p', 's', str(index), raw)
            documents.append((tokens, ref, raw))
            m.record('other', 's', str(index), b'alpha beta gamma or')
        queries = ['alpha', 'beta gamma', 'ALPHA beta', 'alpha OR beta', '"alpha"* -gamma',
                   'absent alpha', 'alpha alpha', 'alpha; beta', 'or', '', '!*']
        for mode, query, limit in itertools.product(('all', 'any'), queries, (1, 3, 100)):
            wanted = set(re.findall(r'\w+', query.casefold()))
            expected = [(ref, raw) for tokens, ref, raw in reversed(documents)
                        if wanted and (wanted <= tokens if mode == 'all' else bool(wanted & tokens))][:limit]
            actual = m.search('p', query, limit, mode)
            assert [r['record_hash'] for r in actual] == [r['record_hash'] for r, _ in expected], (mode, query, limit)
            assert all(r['project'] == 'p' for r in actual)
            if actual:
                recovered = m.retrieve('p', [r['record_hash'] for r in actual])
                assert [r['raw'] for r in recovered] == [raw for _, raw in expected]
            if mode == 'all':
                assert actual == m.search('p', query, limit)
            checked += 1
        for mode in (None, True, False, [], {}, '', 'ANY', 'other'):
            for query in ('', 'alpha'):
                try: m.search('p', query, match_mode=mode)
                except ValueError: pass
                else: raise AssertionError(('Invalid mode accepted', mode))
                checked += 1
        for mode in ('all', 'any'):
            for query, limit in [(None, 10), ([], 10), ('alpha', 0), ('alpha', True), ('alpha', 101)]:
                try: m.search('p', query, limit, mode)
                except ValueError: pass
                else: raise AssertionError(('Existing validation weakened', query, limit))
                checked += 1
            damaged = Memory(Store(Path(folder) / mode))
            damaged.record('p', 's', '1', b'alpha beta')
            with damaged.db() as db: db.execute('DELETE FROM search')
            try: damaged.search('p', 'alpha', match_mode=mode)
            except ValueError: pass
            else: raise AssertionError('Corrupt index treated as a valid empty result')
            checked += 1
        return {'finite_cases': checked, 'store_io': dict(m.store.metrics), 'memory_metrics': dict(m.metrics)}


if __name__ == '__main__':
    import json
    print(json.dumps(check(sys.argv[1])))
