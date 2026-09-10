import copy
import itertools
import unittest
from planner import merge_windows

class IntegerSubclass(int):
    pass

class MergeWindowsChecks(unittest.TestCase):
    def test_e13_and_transitive_overlap(self):
        self.assertEqual(merge_windows([(1, 3), (3, 5)]), [(1, 3), (3, 5)])
        self.assertEqual(merge_windows([(1, 3), (3, 5)], True), [(1, 5)])
        self.assertEqual(merge_windows([(8, 10), (1, 4), (3, 7), (6, 9)]), [(1, 10)])
        self.assertEqual(merge_windows([(1, 8), (2, 3), (1, 8)]), [(1, 8)])

    def test_validation(self):
        invalid = [None, 1, True, '12', {}, set(), iter([]),
                   [1], ['12'], [{1, 2}], [(1,)], [(1, 2, 3)],
                   [(1, 1)], [(2, 1)], [(False, 2)], [(0, True)],
                   [(1.0, 2)], [(1, 2.0)], [('1', 2)], [(1, None)],
                   [(IntegerSubclass(1), 2)], [(1, 2), (3, 3)]]
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    merge_windows(value)
        for flag in [0, 1, None, 'false', [], {}, 0.0]:
            with self.subTest(flag=repr(flag)):
                with self.assertRaises(ValueError):
                    merge_windows([], flag)

    def test_exact_integers_and_empty(self):
        big = 10 ** 100
        self.assertEqual(merge_windows([(big + 1, big + 3), (big, big + 2)]), [(big, big + 3)])
        self.assertEqual(merge_windows([(-big, -big + 2), (-big + 2, -big + 4)]),
                         [(-big, -big + 2), (-big + 2, -big + 4)])
        for empty in [[], ()]:
            for flag in [False, True]:
                self.assertEqual(merge_windows(empty, flag), [])

    def test_input_preservation_and_output_types(self):
        for windows in [[[5, 8], [1, 4], [3, 6]], ([5, 8], (1, 4), [3, 6])]:
            before = copy.deepcopy(windows)
            identities = [id(w) for w in windows]
            for flag in [False, True]:
                result = merge_windows(windows, flag)
                self.assertEqual(result, [(1, 8)])
                self.assertIs(type(result), list)
                self.assertTrue(all(type(w) is tuple for w in result))
                self.assertEqual(windows, before)
                self.assertEqual([id(w) for w in windows], identities)
        invalid = [[5, 8], [1, 4], [3, 3]]
        before = copy.deepcopy(invalid)
        with self.assertRaises(ValueError):
            merge_windows(invalid)
        self.assertEqual(invalid, before)

    def test_exhaustive_against_connected_components(self):
        # Independent oracle: components of the pairwise overlap graph.
        intervals = list(itertools.combinations(range(-2, 3), 2))
        cases = 0
        for length in range(4):
            for windows in itertools.product(intervals, repeat=length):
                for touching in [False, True]:
                    pending = set(range(length))
                    expected = []
                    while pending:
                        component = {pending.pop()}
                        frontier = list(component)
                        while frontier:
                            a = windows[frontier.pop()]
                            for j in list(pending):
                                b = windows[j]
                                lo, hi = max(a[0], b[0]), min(a[1], b[1])
                                if lo < hi or (touching and lo == hi):
                                    pending.remove(j)
                                    component.add(j)
                                    frontier.append(j)
                        expected.append((min(windows[j][0] for j in component),
                                         max(windows[j][1] for j in component)))
                    self.assertEqual(merge_windows(windows, touching), sorted(expected))
                    cases += 1
        self.assertEqual(cases, 2222)
        print(f'Independent oracle: {cases} cases passed')

unittest.main(verbosity=2)
