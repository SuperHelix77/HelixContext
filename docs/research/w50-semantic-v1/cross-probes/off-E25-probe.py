from copy import deepcopy
from itertools import combinations, combinations_with_replacement
from planner import merge_windows

class IntSubclass(int):
    pass

invalid = [None, 1, True, '12', {}, iter([]), [None], [1], [[]], [[1]],
           [[1, 2, 3]], ['12'], [{1, 2}], [[True, 2]], [[0, False]],
           [[1.0, 2]], [[1, '2']], [[IntSubclass(1), 2]], [[2, 2]], [[3, 2]],
           [[0, 1], [4, 3]]]
invalid_count = 0
for windows in invalid:
    before = deepcopy(windows) if isinstance(windows, (list, tuple)) else None
    try:
        merge_windows(windows)
    except ValueError:
        invalid_count += 1
    else:
        raise AssertionError(f'accepted invalid input: {windows!r}')
    if before is not None:
        assert windows == before
for flag in [None, 0, 1, 'False', [], {}, IntSubclass(1)]:
    try:
        merge_windows([], flag)
    except ValueError:
        invalid_count += 1
    else:
        raise AssertionError(f'accepted invalid flag: {flag!r}')

def reference(windows, touching):
    pending = set(range(len(windows)))
    result = []
    while pending:
        component = {pending.pop()}
        while True:
            added = {j for j in pending if any(
                max(windows[i][0], windows[j][0]) < min(windows[i][1], windows[j][1])
                or (touching and max(windows[i][0], windows[j][0]) == min(windows[i][1], windows[j][1]))
                for i in component)}
            if not added:
                break
            component.update(added)
            pending.difference_update(added)
        result.append((min(windows[i][0] for i in component),
                       max(windows[i][1] for i in component)))
    return sorted(result)

cases = 0
intervals = list(combinations(range(-2, 3), 2))
for size in range(4):
    for sample in combinations_with_replacement(intervals, size):
        for touching in (False, True):
            for windows in ([list(w) for w in reversed(sample)], tuple(reversed(sample))):
                before = deepcopy(windows)
                actual = merge_windows(windows, touching)
                assert actual == reference(windows, touching), (windows, touching, actual)
                assert windows == before
                assert type(actual) is list and all(type(w) is tuple for w in actual)
                cases += 1
huge = 10**100
windows = [[huge + 2, huge + 5], [huge, huge + 3], [-huge, -huge + 1]]
assert merge_windows(windows) == [(-huge, -huge + 1), (huge, huge + 5)]
assert merge_windows([(1, 3), (3, 5)]) == [(1, 3), (3, 5)]
result = merge_windows(windows)
result.append((0, 1))
assert len(windows) == 3
print(f'Additional checks passed: {cases} exhaustive graph-reference cases; {invalid_count} invalid-input cases; exact large integers, default adjacency, and output independence.')
