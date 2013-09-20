import macropy.activate
from smt.Z3 import *
import unittest

class TestZ3(unittest.TestCase):
  def setUp(self):
    self.s = Z3()

  def test_sat_ints(self):
    x = self.s.getIntVar('x')
    self.s.solverAssert(x > 0)
    self.s.solverAssert(x < 2)
    self.assertEqual(self.s.check(), Z3.Sat)

  def test_unsat_ints(self):
    x = self.s.getIntVar('x')
    self.s.solverAssert(x > 2)
    self.s.solverAssert(x < 2)
    self.assertEqual(self.s.check(), Z3.Unsat)

  def test_multiple_vars(self):
    x0 = self.s.getIntVar('x')
    x1 = self.s.getIntVar('x')
    self.s.solverAssert(x0 > 2)
    self.s.solverAssert(x1 < 2)
    self.assertEqual(self.s.check(), Z3.Unsat)

if __name__ == '__main__':
    unittest.main()
