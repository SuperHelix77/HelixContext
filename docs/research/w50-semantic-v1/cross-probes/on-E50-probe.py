import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import planner


class WritePlanTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / 'plan.json'
        self.old = b'previous exact bytes\x00\xff\r\n'
        self.rows = [{
            'inventory_tag': ' PKG\t ',
            'label_exact': 'cafe\u0301 / Ω / 箱 \t ',
            'sequence_exact': '0000000081700321',
            'windows': [[3, 5], [1, 3], [2, 4], [8, 10], [10, 12]],
        }]

    def assert_destination(self, existed):
        if existed:
            self.assertEqual(self.path.read_bytes(), self.old)
        else:
            self.assertFalse(self.path.exists())
        self.assertEqual(set(self.root.iterdir()), {self.path} if existed else set())

    def test_invalid_batches_preserve_existing_and_absent_destinations(self):
        invalid_batches = [None, {}, [None], [[]], [{}]]
        for field in self.rows[0]:
            missing = copy.deepcopy(self.rows[0])
            del missing[field]
            invalid_batches.append([self.rows[0], missing])
        for field in ('inventory_tag', 'label_exact', 'sequence_exact'):
            for value in (None, 0, True, []):
                invalid_batches.append([self.rows[0], {**self.rows[0], field: value}])
        for windows in (None, [(3, 2)], [(1, 1)], [(True, 3)], [(1, 2.0)]):
            invalid_batches.append([self.rows[0], {**self.rows[0], 'windows': windows}])
        for existed in (False, True):
            for rows in invalid_batches:
                with self.subTest(existed=existed, rows=rows):
                    if existed:
                        self.path.write_bytes(self.old)
                    before = copy.deepcopy(rows)
                    with self.assertRaises(ValueError):
                        planner.write_plan(self.path, rows)
                    self.assertEqual(rows, before)
                    self.assert_destination(existed)

    def test_success_preserves_exact_values_and_inputs(self):
        before = copy.deepcopy(self.rows)
        for existed in (False, True):
            with self.subTest(existed=existed):
                if existed:
                    self.path.write_bytes(self.old)
                planner.write_plan(self.path, tuple(self.rows))
                result = json.loads(self.path.read_text(encoding='utf-8'))
                self.assertEqual(result, [{**before[0], 'windows': [[1, 5], [8, 10], [10, 12]]}])
                self.assertEqual(self.rows, before)
                self.assertEqual(set(self.root.iterdir()), {self.path})

    def test_empty_plan(self):
        planner.write_plan(self.path, [])
        self.assertEqual(json.loads(self.path.read_bytes()), [])

    def test_publication_uses_complete_closed_sibling_file(self):
        self.path.write_bytes(self.old)
        real_replace = os.replace
        real_dump = json.dump
        streams = []

        def capture_dump(value, stream, **kwargs):
            streams.append(stream)
            return real_dump(value, stream, **kwargs)

        def inspect_replace(source, destination):
            self.assertEqual(Path(source).parent, self.path.parent)
            self.assertEqual(Path(destination), self.path)
            self.assertTrue(streams[0].closed)
            self.assertEqual(self.path.read_bytes(), self.old)
            self.assertEqual(json.loads(Path(source).read_bytes()),
                             json.loads(json.dumps(planner.build_plan(self.rows))))
            real_replace(source, destination)

        with self.path.open('rb') as old_reader:
            with patch('planner.json.dump', side_effect=capture_dump):
                with patch('planner.os.replace', side_effect=inspect_replace) as replace:
                    planner.write_plan(self.path, self.rows)
                    replace.assert_called_once()
            self.assertEqual(old_reader.read(), self.old)
        self.assertEqual(len(json.loads(self.path.read_bytes())), 1)
        self.assertEqual(set(self.root.iterdir()), {self.path})

    def test_io_failures_propagate_and_clean_up(self):
        def partial_write_failure(value, stream, **kwargs):
            stream.write('[{"partial":')
            raise OSError('injected partial write failure')

        failures = [
            ('planner.json.dump', partial_write_failure),
            ('planner.os.fsync', OSError('injected sync failure')),
            ('planner.os.replace', OSError('injected replace failure')),
            ('planner.tempfile.NamedTemporaryFile', OSError('injected creation failure')),
        ]
        before = copy.deepcopy(self.rows)
        for existed in (False, True):
            for target, failure in failures:
                with self.subTest(existed=existed, target=target):
                    if existed:
                        self.path.write_bytes(self.old)
                    with patch(target, side_effect=failure):
                        with self.assertRaisesRegex(OSError, 'injected'):
                            planner.write_plan(self.path, self.rows)
                    self.assert_destination(existed)
                    self.assertEqual(self.rows, before)

    def test_real_replace_failure_preserves_directory(self):
        self.path.mkdir()
        marker = self.path / 'keep'
        marker.write_bytes(self.old)
        with self.assertRaises(OSError):
            planner.write_plan(self.path, self.rows)
        self.assertEqual(marker.read_bytes(), self.old)
        self.assertEqual(set(self.root.iterdir()), {self.path})

    def test_missing_parent_failure(self):
        with self.assertRaises(FileNotFoundError):
            planner.write_plan(self.root / 'missing' / 'plan.json', self.rows)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
