'''
This tests code after the macro transformation.

Before the transformation, there would be calls to mkLabel and restrict but
the jifs should be gone. It would also 
'''
#import macropy.activate
from smt.Z3 import *
import unittest
import JeevesGlobal
import JeevesLib

class TestJeevesConfidentiality(unittest.TestCase):
  def setUp(self):
    self.s = Z3()
    # reset the Jeeves state
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

  def test_restrict_with_sensitivevalue(self):
    x = JeevesGlobal.jeevesLib.mkLabel('x')
    JeevesGlobal.jeevesLib.restrict(x, lambda y: y == 2)
    value = JeevesGlobal.jeevesLib.mkSensitive(x, 42, 41)

    valueConcrete = JeevesGlobal.jeevesLib.concretize(2, value)
    self.assertEquals(valueConcrete, 42)

    valueConcrete = JeevesGlobal.jeevesLib.concretize(1, value)
    self.assertEquals(valueConcrete, 41)

  def test_restrict_with_cyclic(self):
    jl = JeevesGlobal.jeevesLib

    # use the value itself as the context
    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    value = jl.mkSensitive(x, 42, 20)
    self.assertEquals(jl.concretize(value, value), 42)

    value = jl.mkSensitive(x, 41, 20)
    self.assertEquals(jl.concretize(value, value), 20)

  def test_jif_with_ints(self):
    jl = JeevesGlobal.jeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    a = jl.jif(x, lambda:13, lambda:17 )
    self.assertEquals(jl.concretize(42, a), 13)
    self.assertEquals(jl.concretize(-2, a), 17)

    b = jl.jif(True, lambda:13, lambda:17)
    self.assertEquals(jl.concretize(42, b), 13)
    self.assertEquals(jl.concretize(-2, b), 13)

    c = jl.jif(False, lambda:13, lambda:17)
    self.assertEquals(jl.concretize(42, c), 17)
    self.assertEquals(jl.concretize(-2, c), 17)

    conditional = jl.mkSensitive(x, True, False)
    d = jl.jif(conditional, lambda:13, lambda:17)
    self.assertEquals(jl.concretize(42, d), 13)
    self.assertEquals(jl.concretize(-2, d), 17)

    conditional = jl.mkSensitive(x, False, True)
    d = jl.jif(conditional, lambda:13, lambda:17)
    self.assertEquals(jl.concretize(42, d), 17)
    self.assertEquals(jl.concretize(-2, d), 13)

    y = jl.mkLabel('y')
    z = jl.mkLabel('z')
    jl.restrict(y, lambda (a,_) : a)
    jl.restrict(z, lambda (_,a) : a)
    faceted_int = jl.mkSensitive(y, 10, 0)
    conditional = faceted_int > 5
    i1 = jl.mkSensitive(z, 101, 102)
    i2 = jl.mkSensitive(z, 103, 104)
    f = jl.jif(conditional, lambda:i1, lambda:i2)
    self.assertEquals(jl.concretize((True, True), f),101)
    self.assertEquals(jl.concretize((True, False), f), 102)
    self.assertEquals(jl.concretize((False, True), f), 103)
    self.assertEquals(jl.concretize((False, False), f), 104)

  def test_jif_with_objects(self):
    return NotImplemented

  def test_restrict_under_conditional(self):
    jl = JeevesGlobal.jeevesLib

    x = jl.mkLabel('x')
    def yes_restrict():
        jl.restrict(x, lambda ctxt : ctxt == 1)
    def no_restrict():
        pass

    value = jl.mkSensitive(x, 42, 0)
    jl.jif(value == 42, yes_restrict, no_restrict)
    self.assertEquals(jl.concretize(0, value), 0)
    self.assertEquals(jl.concretize(1, value), 42)

    y = jl.mkLabel('y')
    def yes_restrict():
        jl.restrict(y, lambda ctxt : ctxt == 1)
    def no_restrict():
        pass

    value = jl.mkSensitive(y, 43, 0)
    jl.jif(value == 42, yes_restrict, no_restrict)
    self.assertEquals(jl.concretize(0, value), 43)
    self.assertEquals(jl.concretize(1, value), 43)

  def test_nested_conditionals_no_shared_path(self):
    return NotImplemented

  def test_nested_conditionals_shared_path(self):
    return NotImplemented

  def test_jif_with_assign(self):
    return NotImplemented

  def function_facets(self):
    return NotImplemented

if __name__ == '__main__':
    unittest.main()
