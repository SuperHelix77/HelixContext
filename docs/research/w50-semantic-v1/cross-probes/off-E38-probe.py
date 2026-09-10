from copy import deepcopy
from planner import build_plan, merge_windows

base = {'inventory_tag': ' tag\t ', 'label_exact': 'cafe\u0301 / Ω / 箱\t ',
        'sequence_exact': '0000000081700321', 'windows': [[8, 10], [1, 3], [2, 4], [10, 12]]}
empty = dict.fromkeys(('inventory_tag', 'label_exact', 'sequence_exact'), '')
empty['windows'] = []
rows = [dict(base, extra='discard'), empty, dict(base, inventory_tag='last')]
valid_cases = 0
for source in (rows, tuple(rows), [], ()):
    before = deepcopy(source)
    output = build_plan(source)
    assert source == before
    assert len(output) == len(source)
    for original, planned in zip(source, output):
        assert set(planned) == {'inventory_tag', 'label_exact', 'sequence_exact', 'windows'}
        assert planned is not original
        for key in ('inventory_tag', 'label_exact', 'sequence_exact'):
            assert planned[key] == original[key] and isinstance(planned[key], str)
        assert planned['windows'] == merge_windows(original['windows'])
        assert planned['windows'] is not original['windows']
    valid_cases += 1
output = build_plan(rows)
output[0]['windows'].append((20, 30))
output[0]['inventory_tag'] = 'changed'
assert rows[0] == dict(base, extra='discard')

bad = [None, {}, 'rows', 1, iter([]), [None], [[]], ['row'], [1], [{}]]
for key in base:
    bad.append([{k: v for k, v in base.items() if k != key}])
for key in ('inventory_tag', 'label_exact', 'sequence_exact'):
    for value in (None, 0, True, [], {}, b'text'):
        bad.append([dict(base, **{key: value})])
for windows in (None, {}, '12', [[1]], [[1, 2, 3]], [[True, 2]], [[1, 1]], [[3, 2]], [[1.0, 2]]):
    bad.append([dict(base, windows=windows)])
bad.append([base, dict(base, label_exact=None)])
for source in bad:
    before = deepcopy(source) if isinstance(source, (list, tuple)) else None
    try:
        build_plan(source)
    except ValueError:
        pass
    else:
        raise AssertionError(f'accepted invalid rows: {source!r}')
    if before is not None:
        assert source == before
print(f'Additional build_plan checks passed: {valid_cases} valid container cases, {len(bad)} invalid cases; exact strings, empty strings, row order, exact output keys, and input/output independence.')
