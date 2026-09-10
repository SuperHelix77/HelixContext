import unittest
import solution as s

class Public(unittest.TestCase):
    def test_replay(self):
        e={'id':'x','account':'a','delta':2}; b={'a':3}
        self.assertEqual(s.apply_batch(b,[e,e]),{'a':5}); self.assertEqual(b,{'a':3})
    def test_order(self):
        e=[{'id':'x','account':'a','delta':-1},{'id':'y','account':'a','delta':2}]
        with self.assertRaises(ValueError): s.apply_batch({},e)
    def test_conflict(self):
        with self.assertRaises(ValueError): s.apply_batch({},[{'id':'x','account':'a','delta':1},{'id':'x','account':'b','delta':1}])
    def test_invalid(self):
        for b,e in [({'a':True},[]),({},[{'id':'x','account':'a','delta':True}]),({},None)]:
            with self.assertRaises(ValueError): s.apply_batch(b,e)
