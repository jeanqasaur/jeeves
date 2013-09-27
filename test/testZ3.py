import macropy.activate
from smt.Z3 import *
from fast import AST
import unittest

class TestZ3(unittest.TestCase):
  def setUp(self):
    self.s = Z3()

  def test_sat_ints(self):
    x = self.s.getIntVar('x')
    self.s.solverAssert(x > 0)
    self.s.solverAssert(x < 2)
    self.assertTrue(self.s.isSatisfiable())

  def test_unsat_ints(self):
    x = self.s.getIntVar('x')
    self.s.solverAssert(x > 2)
    self.s.solverAssert(x < 2)
    self.assertFalse(self.s.isSatisfiable())

  def test_multiple_vars(self):
    x0 = self.s.getIntVar('x')
    x1 = self.s.getIntVar('x')
    self.s.solverAssert(x0 > 2)
    self.s.solverAssert(x1 < 2)
    self.assertFalse(self.s.isSatisfiable())

  def test_multiple_vars2(self):
    x0 = self.s.getIntVar('x')
    x1 = self.s.getIntVar('y')
    self.s.solverAssert(x0 > 2)
    self.s.solverAssert(x1 < 2)
    self.assertTrue(self.s.isSatisfiable())

  def test_ast(self):
    b1 = AST.Var('x')
    b2 = AST.Var('x')
    # should be a different var even if the user accidentally has a name collision

    t = AST.Facet(b1, 1, 10) + AST.Facet(b2, 100, 1000)

    self.assertTrue(self.s.isSatisfiable())

    self.s.push()
    self.s.boolExprAssert(t == 101)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 1001)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 110)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 1010)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 11)
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 1001)
    self.s.boolExprAssert(t == 1010)
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t == 1001)
    self.s.boolExprAssert(AST.Not(b1))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t - 1 == 1009)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t - 1 == 1008)
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t * 2 == 2002)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(t * 2 == 2004)
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

  def test_ast_bools(self):
    b1 = AST.Var()
    b2 = AST.Var()
    b3 = AST.Var()
    b4 = AST.Var()

    self.s.push()
    self.s.boolExprAssert(AST.And(b1, b2))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.And(b1, b2))
    self.s.boolExprAssert(AST.Not(b1))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Or(b1, b2))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Or(b1, b2))
    self.s.boolExprAssert(AST.Not(b1))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Or(b1, b2))
    self.s.boolExprAssert(AST.Not(b1))
    self.s.boolExprAssert(AST.Not(b2))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Or(b1, b2))
    self.s.boolExprAssert(AST.And(AST.Not(b1),AST.Not(b2)))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.And(AST.Or(b1, b2),AST.And(AST.Not(b1),AST.Not(b2))))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Implies(b1, b2))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Implies(b1, b2))
    self.s.boolExprAssert(b1)
    self.s.boolExprAssert(b2)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Implies(b1, b2))
    self.s.boolExprAssert(b1)
    self.s.boolExprAssert(AST.Not(b2))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Implies(b1, b2))
    self.s.boolExprAssert(AST.Not(b1))
    self.s.boolExprAssert(b2)
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Implies(b1, b2))
    self.s.boolExprAssert(AST.Not(b1))
    self.s.boolExprAssert(AST.Not(b2))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

  def test_ast_comparisons(self):
    b1 = AST.Var()
    b2 = AST.Var()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 0, 1) != AST.Facet(b1, 1, 2) - 1)
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 0, 1) < AST.Facet(b2, 3, 4))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 0, 1) <= AST.Facet(b2, 3, 4))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 0, 1) < AST.Facet(b2, -1, 0))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 0, 1) <= AST.Facet(b2, -1,0))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 3, 4) > AST.Facet(b2, 0, 1))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, 3, 4) >= AST.Facet(b2, 0, 1))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, -1, 0) > AST.Facet(b2, 0, 1))
    self.assertFalse(self.s.isSatisfiable())
    self.s.pop()

    self.s.push()
    self.s.boolExprAssert(AST.Facet(b1, -1, 0) >= AST.Facet(b2, 0, 1))
    self.assertTrue(self.s.isSatisfiable())
    self.s.pop()

if __name__ == '__main__':
    unittest.main()
