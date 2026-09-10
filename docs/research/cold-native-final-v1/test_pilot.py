import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('cold_native_pilot', Path(__file__).with_name('pilot.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


class PacketTests(unittest.TestCase):
    def test_exact_reopened_packet(self):
        f = p.fixture.fixtures()['cold']
        source = json.dumps(f['source'], ensure_ascii=False).encode()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); packet = p.recover(root, f['task'], source)
            want = p.fixture.expected('cold', f)
            self.assertTrue(p.fixture.equal(packet['recovered_fields'], want))
            self.assertTrue(packet['original_note']['label_exact'].endswith(' \t '))
            self.assertIn('e\u0301', packet['original_note']['label_exact'])
            receipt = p.read(root / 'recovery.json')
            self.assertEqual(receipt['reopened_recovery_io']['object_bytes_read'], len(source))
            self.assertEqual(receipt['reopened_recovery_io']['object_read_operations'], 1)
            self.assertEqual(p.grade(json.dumps(want), want), want)
            self.assertEqual(p.grade('```json\n' + json.dumps(want) + '\n```', want), want)

    def test_unknown_and_inherited_do_not_prepare(self):
        f = p.fixture.fixtures()['cold']; source = json.dumps(f['source']).encode()
        for task, constraints in [(f['task'] + ' also interpret all possible policies', ()),
                                  (f['task'], ('Only disclose with consent',))]:
            with self.subTest(task=task), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                with self.assertRaises(ValueError): p.recover(root, task, source, constraints)
                self.assertFalse((root / 'packet.json').exists())

    def test_final_fidelity_mutants_fail(self):
        want = p.fixture.expected('cold', p.fixture.fixtures()['cold'])
        mutants = [{**want, 'label_exact': want['label_exact'].rstrip()},
                   {**want, 'evidence_turn': True}, {**want, 'sequence_exact': int(want['sequence_exact'])},
                   {**want, 'label_utf8_base64': 'wrong'}, {**want, 'extra': 1}]
        for mutant in mutants:
            with self.subTest(mutant=mutant), self.assertRaises(ValueError): p.grade(json.dumps(mutant), want)
        duplicate = json.dumps(want)[:-1] + ', "evidence_turn": 1}'
        with self.assertRaises(ValueError): p.grade(duplicate, want)


if __name__ == '__main__': unittest.main()
