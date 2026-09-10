import unittest
import solution as s

class Public(unittest.TestCase):
    def test_order(self):
        self.assertEqual(s.schedule({'a':['z'],'b':[]}), ['b','z','a'])
    def test_duplicate_dependency(self):
        self.assertEqual(s.schedule({'b':['a','a']}), ['a','b'])
    def test_empty(self):
        self.assertEqual(s.schedule({}), [])
    def test_cycle(self):
        with self.assertRaises(ValueError): s.schedule({'a':['b'],'b':['a']})
    def test_invalid(self):
        for x in [None, {'a':'b'}, {'':[]}, {'a':[False]}]:
            with self.assertRaises(ValueError): s.schedule(x)
