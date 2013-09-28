'''
This tests code after the macro transformation.

Before the transformation, there would be calls to mkLabel and restrict but
the jifs should be gone. It would also 
'''
import macropy.activate
from smt.Z3 import *
import unittest
import JeevesGlobal
import JeevesLib

class TestJeevesConfidentiality(unittest.TestCase):
  def setUp(self):
    self.s = Z3()
    # rest the Jeeves state
    JeevesGlobal.set_jeeves_state(JeevesLib.JeevesLib())

  def test_restrict_all_permissive(self):
    x = JeevesGlobal.jeevesLib.mkLabel('x')
    JeevesGlobal.jeevesLib.restrict(x, lambda _: True)
    xConcrete = JeevesGlobal.jeevesLib.concretize(None, x)
    # make sure that concretizing x allows everyone to see
    self.assertTrue(xConcrete)

  def test_restrict_all_restrictive(self):
    x = JeevesGlobal.jeevesLib.mkLabel('x')
    JeevesGlobal.jeevesLib.restrict(x, lambda _: False)
    xConcrete = JeevesGlobal.jeevesLib.concretize(None, x)
    self.assertFalse(xConcrete)

  def test_restrict_with_context(self):
    x = JeevesGlobal.jeevesLib.mkLabel('x')
    JeevesGlobal.jeevesLib.restrict(x, lambda y: y == 2)

    xConcrete = JeevesGlobal.jeevesLib.concretize(2, x)
    self.assertTrue(xConcrete)

    xConcrete = JeevesGlobal.jeevesLib.concretize(3, x)
    self.assertFalse(xConcrete)

  def test_jif_with_ints(self):
    return NotImplemented

  def test_jif_with_objects(self):
    return NotImplemented

  def test_restrict_under_conditional(self):
    return NotImplemented

  def test_nested_conditionals_no_shared_path(self):
    return NotImplemented

  def test_nested_conditionals_shared_path(self):
    return NotImplemented

  def function_facets(self):
    return NotImplemented

if __name__ == '__main__':
    unittest.main()
