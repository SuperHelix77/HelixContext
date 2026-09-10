import unittest
import solution as s

class Public(unittest.TestCase):
    def test_merge(self):
        self.assertEqual(s.normalize([(5,9),(0,2),(2,5),(3,3)]), [(0,9)])
    def test_empty(self):
        self.assertEqual(s.normalize(iter([])), [])
    def test_no_mutation(self):
        x=[[3,4],[0,1]]; self.assertEqual(s.normalize(x),[(0,1),(3,4)])
        self.assertEqual(x,[[3,4],[0,1]])
    def test_invalid(self):
        for x in [None, [(2,1)], [(False,3)], [(0,1.0)], [[1]]]:
            with self.assertRaises(ValueError): s.normalize(x)
