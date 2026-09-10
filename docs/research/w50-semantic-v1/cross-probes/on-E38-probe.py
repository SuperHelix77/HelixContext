import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from planner import build_plan, merge_windows

FIELDS = {'inventory_tag', 'label_exact', 'sequence_exact', 'windows'}
BASE = {'inventory_tag': ' tag\t ', 'label_exact': 'cafe\u0301 / Ω / 箱 \t ',
        'sequence_exact': '0000000081700321', 'windows': [[3, 5], [1, 3], [2, 4]]}

class IntegrationChecks(unittest.TestCase):
    def test_exact_strings_order_keys_and_no_mutation(self):
        empty = dict.fromkeys(('inventory_tag', 'label_exact', 'sequence_exact'), '')
        empty['windows'] = ()
        rows = [{**copy.deepcopy(BASE), 'extra': 'ignore'}, empty]
        for container in (rows, tuple(rows)):
            before = copy.deepcopy(container)
            result = build_plan(container)
            self.assertIs(type(result), list)
            self.assertEqual(container, before)
            self.assertEqual(len(result), 2)
            for original, plan in zip(container, result):
                self.assertEqual(set(plan), FIELDS)
                self.assertIsNot(plan, original)
                for field in FIELDS - {'windows'}:
                    self.assertEqual(list(map(ord, plan[field])), list(map(ord, original[field])))
            self.assertEqual(result[0]['windows'], [(1, 5)])
            self.assertEqual(result[1]['windows'], [])
            result[0]['windows'].append((20, 30))
            self.assertEqual(container, before)

    def test_empty_inputs(self):
        self.assertEqual(build_plan([]), [])
        self.assertEqual(build_plan(()), [])

    def test_invalid_rows_and_missing_fields(self):
        for rows in (None, {}, 'rows', 1, iter([]), [None], [[]], ['row'], [1]):
            with self.subTest(rows=repr(rows)), self.assertRaises(ValueError):
                build_plan(rows)
        for field in FIELDS:
            row = copy.deepcopy(BASE)
            del row[field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                build_plan([row])
        for field in FIELDS - {'windows'}:
            for value in (None, 0, True, 1.2, b'text', [], {}):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    build_plan([{**BASE, field: value}])

    def test_invalid_windows_and_failure_preserves_inputs(self):
        for windows in (None, {}, 'windows', [(1,)], [(1, 2, 3)], [(2, 2)],
                        [(3, 1)], [(True, 3)], [(1, False)], [(1.0, 3)], [(1, '3')]):
            rows = [copy.deepcopy(BASE), {**copy.deepcopy(BASE), 'windows': windows}]
            before = copy.deepcopy(rows)
            with self.subTest(windows=windows), self.assertRaises(ValueError):
                build_plan(rows)
            self.assertEqual(rows, before)

    def test_merge_delegation(self):
        with patch('planner.merge_windows', wraps=merge_windows) as merge:
            result = build_plan([BASE])
            merge.assert_called_once_with(BASE['windows'])
            self.assertEqual(result[0]['windows'], [(1, 5)])

    def test_merge_regression(self):
        big = 10 ** 100
        self.assertEqual(merge_windows([(big, big+2), (big+1, big+3)]), [(big, big+3)])
        self.assertEqual(merge_windows([(6, 9), (1, 4), (3, 7)]), [(1, 9)])
        self.assertEqual(merge_windows([(1, 3), (3, 5)]), [(1, 3), (3, 5)])
        self.assertEqual(merge_windows([(1, 3), (3, 5)], True), [(1, 5)])
        for flag in (0, 1, None, 'True'):
            with self.assertRaises(ValueError):
                merge_windows([], flag)

    def test_delivered_plan_against_history(self):
        history = json.loads(Path('history.json').read_text())
        notes = next(e['data']['notes'] for e in history if e['event_id'] == 'E01')
        original = next(n for n in notes if n['inventory_tag'] == 'PKG_01_01')
        plan = json.loads(Path('plan.json').read_text(encoding='utf-8'))
        self.assertEqual(plan, [{**original, 'windows': [[1, 5], [8, 10], [10, 12]]}])
        for field in FIELDS - {'windows'}:
            self.assertEqual(plan[0][field].encode('utf-8'), original[field].encode('utf-8'))
        self.assertIn('\u0301', plan[0]['label_exact'])
        self.assertTrue(plan[0]['label_exact'].endswith(' \t '))
        self.assertEqual(plan[0]['sequence_exact'], '0000000081700321')

unittest.main(verbosity=2)
