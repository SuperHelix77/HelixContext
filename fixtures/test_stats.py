import unittest
from stats import weighted_mean
class TestWeightedMean(unittest.TestCase):
 def test_value(self): self.assertEqual(weighted_mean([2,8],[1,3]),6.5)
 def test_empty(self): self.assertIsNone(weighted_mean([],[]))
 def test_zero(self): self.assertIsNone(weighted_mean([2,8],[0,0]))
 def test_mismatch(self):
  with self.assertRaises(ValueError): weighted_mean([1,2],[1])
 def test_negative(self):
  with self.assertRaises(ValueError): weighted_mean([1,2],[-1,2])
if __name__=='__main__': unittest.main()
