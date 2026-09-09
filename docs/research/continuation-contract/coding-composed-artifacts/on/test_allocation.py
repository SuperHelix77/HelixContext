import unittest
from allocation import allocate
class TestAllocation(unittest.TestCase):
 def test_remainder(self): self.assertEqual(allocate(5,[1,1,1]),[2,2,1])
 def test_zero(self): self.assertEqual(allocate(0,[1,2]),[0,0])
 def test_empty(self): self.assertEqual(allocate(0,[]),[])
 def test_invalid(self):
  for a,b in [(True,[1]),(-1,[1]),(2,[]),(2,[0]),(2,[-1]),(2,[True])]:
   with self.assertRaises(ValueError): allocate(a,b)
if __name__=='__main__': unittest.main()
