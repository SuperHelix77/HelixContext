import json
import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import planner


class WritePlanTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'plan.json'
        self.previous = b'previous exact bytes\x00\xff\n'
        self.rows = [{
            'inventory_tag': ' tag\t ',
            'label_exact': 'cafe\u0301 / Ω / 箱 \t ',
            'sequence_exact': '0000000081700321',
            'windows': [[8, 10], [1, 3], [2, 4], [10, 12]],
        }]

    def prepare(self, exists):
        self.path.unlink(missing_ok=True)
        if exists:
            self.path.write_bytes(self.previous)

    def assert_unchanged(self, exists):
        if exists:
            self.assertEqual(self.path.read_bytes(), self.previous)
        else:
            self.assertFalse(self.path.exists())
        self.assertEqual(set(self.path.parent.iterdir()), {self.path} if exists else set())

    def test_invalid_batches_preserve_destination(self):
        invalid = [None, {}, [None], [{}]]
        for field in self.rows[0]:
            invalid.append([{k: v for k, v in self.rows[0].items() if k != field}])
        for field in ('inventory_tag', 'label_exact', 'sequence_exact'):
            invalid.append([dict(self.rows[0], **{field: 1})])
        invalid.append(self.rows + [dict(self.rows[0], windows=[[3, 2]])])
        for exists in (False, True):
            for rows in invalid:
                with self.subTest(exists=exists, rows=rows):
                    self.prepare(exists)
                    before = deepcopy(rows)
                    with self.assertRaises(ValueError):
                        planner.write_plan(self.path, rows)
                    self.assertEqual(rows, before)
                    self.assert_unchanged(exists)

    def test_success_round_trip(self):
        empty_strings = dict.fromkeys(('inventory_tag', 'label_exact', 'sequence_exact'), '')
        empty_strings['windows'] = []
        for exists in (False, True):
            for rows in ([], tuple(self.rows), self.rows + [empty_strings],
                         [dict(self.rows[0], label_exact='\ud800')]):
                with self.subTest(exists=exists, rows=rows):
                    self.prepare(exists)
                    before = deepcopy(rows)
                    self.assertIsNone(planner.write_plan(self.path, rows))
                    expected = json.loads(json.dumps(planner.build_plan(rows)))
                    self.assertEqual(json.loads(self.path.read_text()), expected)
                    self.assertEqual(rows, before)
                    self.assertEqual(set(self.path.parent.iterdir()), {self.path})

    def test_failures_propagate_and_clean_up(self):
        def partial_write(plan, stream, **kwargs):
            stream.write('[partial')
            raise OSError('injected write failure')

        failures = [('json.dump', partial_write), ('os.fsync', OSError('sync failure')),
                    ('os.replace', OSError('replace failure')),
                    ('tempfile.NamedTemporaryFile', OSError('creation failure'))]
        for exists in (False, True):
            for target, failure in failures:
                with self.subTest(exists=exists, target=target):
                    self.prepare(exists)
                    before = deepcopy(self.rows)
                    with patch('planner.' + target, side_effect=failure):
                        with self.assertRaises(OSError):
                            planner.write_plan(self.path, self.rows)
                    self.assertEqual(self.rows, before)
                    self.assert_unchanged(exists)

    def test_complete_same_directory_atomic_replacement(self):
        self.prepare(True)
        replace = os.replace
        expected = json.loads(json.dumps(planner.build_plan(self.rows)))

        def inspect_then_replace(source, destination):
            self.assertEqual(Path(source).parent, self.path.parent)
            self.assertEqual(json.loads(Path(source).read_text()), expected)
            self.assertEqual(self.path.read_bytes(), self.previous)
            replace(source, destination)

        with self.path.open('rb') as old_reader:
            with patch('planner.os.replace', side_effect=inspect_then_replace) as mocked:
                planner.write_plan(self.path, self.rows)
            mocked.assert_called_once()
            self.assertEqual(old_reader.read(), self.previous)
        self.assertEqual(json.loads(self.path.read_text()), expected)
        self.assertEqual(set(self.path.parent.iterdir()), {self.path})


if __name__ == '__main__':
    unittest.main()
