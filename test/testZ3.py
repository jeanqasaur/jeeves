import macropy.activate
from smt.Z3 import *
import unittest

class TestZ3(unittest.TestCase):
  def setUp(self):
    self.s = Z3()

  def test_variable_def(self):
    x = self.s.declareInt('x')
    y = self.s.declareInt('y')
    self.s.solverAssert(x > 0)
    self.s.solverAssert(x < 2)
    self.assertEqual(self.s.check(), Z3.Sat)

if __name__ == '__main__':
    unittest.main()
