import unittest
import macropy.activate
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

class TestSourceTransform(unittest.TestCase):
  def setUp(self):
    # reset the Jeeves state
    JeevesLib.init()

  @jeeves
  def test_restrict_al_permissive(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda _: True)
    xConcrete = JeevesLib.concretize(None, x)
    self.assertTrue(xConcrete)

  @jeeves
  def test_restrict_all_restrictive(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda _: False)
    xConcrete = JeevesLib.concretize(None, x)
    self.assertFalse(xConcrete)

  @jeeves
  def test_restrict_with_context(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda y: y == 2)

    xConcrete = JeevesLib.concretize(2, x)
    self.assertTrue(xConcrete)

    xConcrete = JeevesLib.concretize(3, x)
    self.assertFalse(xConcrete)

  @jeeves
  def test_restrict_with_sensitive_value(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda y: y == 2)
    value = JeevesLib.mkSensitive(x, 42, 41)

    valueConcrete = JeevesLib.concretize(2, value)
    self.assertEquals(valueConcrete, 42)

    valueConcrete = JeevesLib.concretize(1, value)
    self.assertEquals(valueConcrete, 41)

  @jeeves
  def test_restrict_with_cyclic(self):
    jl = JeevesLib

    # use the value itself as the context
    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    value = jl.mkSensitive(x, 42, 20)
    self.assertEquals(jl.concretize(value, value), 42)

    value = jl.mkSensitive(x, 41, 20)
    self.assertEquals(jl.concretize(value, value), 20)

  @jeeves
  def test_jif_with_ints(self):
    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    a = 13 if x else 17
    self.assertEquals(jl.concretize(42, a), 13)
    self.assertEquals(jl.concretize(-2, a), 17)

    b = 13 if True else 17
    self.assertEquals(jl.concretize(42, b), 13)
    self.assertEquals(jl.concretize(-2, b), 13)

    c = 13 if False else 17
    self.assertEquals(jl.concretize(42, c), 17)
    self.assertEquals(jl.concretize(-2, c), 17)

    conditional = jl.mkSensitive(x, True, False)
    d = 13 if conditional else 17
    self.assertEquals(jl.concretize(42, d), 13)
    self.assertEquals(jl.concretize(-2, d), 17)

    conditional = jl.mkSensitive(x, False, True)
    d = 13 if conditional else 17
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
    f = i1 if conditional else i2
    self.assertEquals(jl.concretize((True, True), f),101)
    self.assertEquals(jl.concretize((True, False), f), 102)
    self.assertEquals(jl.concretize((False, True), f), 103)
    self.assertEquals(jl.concretize((False, False), f), 104)

  @jeeves
  def test_restrict(self):
    x = JeevesLib.mkLabel('x')

    value = JeevesLib.mkSensitive(x, 42, 0)
    if value == 42:
      JeevesLib.restrict(x, lambda ctxt : ctxt == 1)
    self.assertEquals(JeevesLib.concretize(0, value), 0)
    self.assertEquals(JeevesLib.concretize(1, value), 42)

    y = JeevesLib.mkLabel('y')

    value = JeevesLib.mkSensitive(y, 43, 0)
    if value == 42:
        JeevesLib.restrict(y, lambda ctxt : ctxt == 1)
    self.assertEquals(JeevesLib.concretize(0, value), 43)
    self.assertEquals(JeevesLib.concretize(1, value), 43)
