'''
This tests code after the macro transformation.

Before the transformation, there would be calls to mkLabel and restrict but
the jifs should be gone. It would also 
'''
#import macropy.activate
import JeevesLib
from smt.Z3 import *
import unittest
from JeevesLib import PositiveVariable, NegativeVariable

class TestJeevesConfidentiality(unittest.TestCase):
  def setUp(self):
    self.s = Z3()
    # reset the Jeeves state
    JeevesLib.init()

  def test_restrict_all_permissive(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda _: True)
    xConcrete = JeevesLib.concretize(None, x)
    # make sure that concretizing x allows everyone to see
    self.assertTrue(xConcrete)

  def test_restrict_all_restrictive(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda _: False)
    xConcrete = JeevesLib.concretize(None, x)
    self.assertFalse(xConcrete)

  def test_restrict_with_context(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda y: y == 2)

    xConcrete = JeevesLib.concretize(2, x)
    self.assertTrue(xConcrete)

    xConcrete = JeevesLib.concretize(3, x)
    self.assertFalse(xConcrete)

  def test_restrict_with_sensitivevalue(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda y: y == 2)
    value = JeevesLib.mkSensitive(x, 42, 41)

    valueConcrete = JeevesLib.concretize(2, value)
    self.assertEquals(valueConcrete, 42)

    valueConcrete = JeevesLib.concretize(1, value)
    self.assertEquals(valueConcrete, 41)

  def test_restrict_with_cyclic(self):
    jl = JeevesLib

    # use the value itself as the context
    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    value = jl.mkSensitive(x, 42, 20)
    self.assertEquals(jl.concretize(value, value), 42)

    value = jl.mkSensitive(x, 41, 20)
    self.assertEquals(jl.concretize(value, value), 20)

  def test_jif_with_ints(self):
    jl = JeevesLib

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
    jl = JeevesLib

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

  def test_jbool_functions_constants(self):
    jl = JeevesLib

    self.assertEquals(jl.jand(lambda:True, lambda:True), True)
    self.assertEquals(jl.jand(lambda:True, lambda:False), False)
    self.assertEquals(jl.jand(lambda:False, lambda:True), False)
    self.assertEquals(jl.jand(lambda:False, lambda:False), False)

    self.assertEquals(jl.jor(lambda:True, lambda:True), True)
    self.assertEquals(jl.jor(lambda:True, lambda:False), True)
    self.assertEquals(jl.jor(lambda:False, lambda:True), True)
    self.assertEquals(jl.jor(lambda:False, lambda:False), False)

    self.assertEquals(jl.jnot(True), False)
    self.assertEquals(jl.jnot(False), True)

  def test_jbool_functions_fexprs(self):
    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda (a,_) : a == 42)

    for lh in (True, False):
      for ll in (True, False):
        for rh in (True, False):
          for rl in (True, False):
            l = jl.mkSensitive(x, lh, ll)
            r = jl.mkSensitive(x, rh, rl)
            self.assertEquals(jl.concretize((42,0), jl.jand(lambda:l, lambda:r)), lh and rh)
            self.assertEquals(jl.concretize((10,0), jl.jand(lambda:l, lambda:r)), ll and rl)
            self.assertEquals(jl.concretize((42,0), jl.jor(lambda:l, lambda:r)), lh or rh)
            self.assertEquals(jl.concretize((10,0), jl.jor(lambda:l, lambda:r)), ll or rl)
            self.assertEquals(jl.concretize((42,0), jl.jnot(l)), not lh)
            self.assertEquals(jl.concretize((10,0), jl.jnot(l)), not ll)

    y = jl.mkLabel('y')
    jl.restrict(y, lambda (_,b) : b == 42)

    for lh in (True, False):
      for ll in (True, False):
        for rh in (True, False):
          for rl in (True, False):
            l = jl.mkSensitive(x, lh, ll)
            r = jl.mkSensitive(y, rh, rl)
            self.assertEquals(jl.concretize((42,0), jl.jand(lambda:l, lambda:r)), lh and rl)
            self.assertEquals(jl.concretize((10,0), jl.jand(lambda:l, lambda:r)), ll and rl)
            self.assertEquals(jl.concretize((42,42), jl.jand(lambda:l, lambda:r)), lh and rh)
            self.assertEquals(jl.concretize((10,42), jl.jand(lambda:l, lambda:r)), ll and rh)

            self.assertEquals(jl.concretize((42,0), jl.jor(lambda:l, lambda:r)), lh or rl)
            self.assertEquals(jl.concretize((10,0), jl.jor(lambda:l, lambda:r)), ll or rl)
            self.assertEquals(jl.concretize((42,42), jl.jor(lambda:l, lambda:r)), lh or rh)
            self.assertEquals(jl.concretize((10,42), jl.jor(lambda:l, lambda:r)), ll or rh)

  def test_nested_conditionals_no_shared_path(self):
    return NotImplemented

  def test_nested_conditionals_shared_path(self):
    return NotImplemented

  def test_jif_with_assign(self):
    jl = JeevesLib

    y = jl.mkLabel('y')
    jl.restrict(y, lambda ctxt : ctxt == 42)

    value0 = jl.mkSensitive(y, 0, 1)
    value2 = jl.mkSensitive(y, 2, 3)

    value = value0
    value = jl.jassign(value, value2)
    self.assertEquals(jl.concretize(42, value), 2)
    self.assertEquals(jl.concretize(10, value), 3)

    value = 100
    value = jl.jassign(value, value2)
    self.assertEquals(jl.concretize(42, value), 2)
    self.assertEquals(jl.concretize(10, value), 3)

    value = value0
    value = jl.jassign(value, 200)
    self.assertEquals(jl.concretize(42, value), 200)
    self.assertEquals(jl.concretize(10, value), 200)

    value = 100
    value = jl.jassign(value, 200)
    self.assertEquals(jl.concretize(42, value), 200)
    self.assertEquals(jl.concretize(10, value), 200)

  def test_jif_with_assign_with_pathvars(self):
    jl = JeevesLib

    x = jl.mkLabel('x')
    y = jl.mkLabel('y')
    jl.restrict(x, lambda (a,_) : a)
    jl.restrict(y, lambda (_,b) : b)

    value0 = jl.mkSensitive(y, 0, 1)
    value2 = jl.mkSensitive(y, 2, 3)

    value = value0
    with PositiveVariable(x):
      value = jl.jassign(value, value2)
    self.assertEquals(jl.concretize((True, True), value), 2)
    self.assertEquals(jl.concretize((True, False), value), 3)
    self.assertEquals(jl.concretize((False, True), value), 0)
    self.assertEquals(jl.concretize((False, False), value), 1)

    value = value0
    with NegativeVariable(x):
      value = jl.jassign(value, value2)
    self.assertEquals(jl.concretize((False, True), value), 2)
    self.assertEquals(jl.concretize((False, False), value), 3)
    self.assertEquals(jl.concretize((True, True), value), 0)
    self.assertEquals(jl.concretize((True, False), value), 1)

  def test_function_facets(self):
    def add1(a):
        return a+1
    def add2(a):
        return a+2

    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt == 42)

    fun = jl.mkSensitive(x, add1, add2)
    value = fun(15)
    self.assertEquals(jl.concretize(42, value), 16)
    self.assertEquals(jl.concretize(41, value), 17)

  def test_objects_faceted(self):
    class TestClass:
      def __init__(self, a, b):
        self.a = a
        self.b = b

    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt)

    y = jl.mkSensitive(x,
      TestClass(1, 2),
      TestClass(3, 4))

    self.assertEquals(jl.concretize(True, y.a), 1)
    self.assertEquals(jl.concretize(True, y.b), 2)
    self.assertEquals(jl.concretize(False, y.a), 3)
    self.assertEquals(jl.concretize(False, y.b), 4)

  def test_objects_mutate(self):
    class TestClass:
      def __init__(self, a, b):
        self.a = a
        self.b = b

    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt)

    s = TestClass(1, None)
    t = TestClass(3, None)
    y = jl.mkSensitive(x, s, t)

    def mut():
      y.a = jl.jassign(y.a, y.a + 100)
    def nonmut():
      pass

    jl.jif(y.a == 1, mut, nonmut)

    self.assertEquals(jl.concretize(True, y.a), 101)
    self.assertEquals(jl.concretize(True, s.a), 101)
    self.assertEquals(jl.concretize(True, t.a), 3)
    self.assertEquals(jl.concretize(False, y.a), 3)
    self.assertEquals(jl.concretize(False, s.a), 1)
    self.assertEquals(jl.concretize(False, t.a), 3)

  def test_objects_methodcall(self):
    class TestClassMethod:
      def __init__(self, a, b):
        self.a = a
        self.b = b
      def add_a_to_b(self):
        self.b = JeevesLib.jassign(self.b, self.a + self.b)
      def return_sum(self):
        return self.a + self.b

    jl = JeevesLib

    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt)

    s = TestClassMethod(1, 10)
    t = TestClassMethod(100, 1000)
    y = jl.mkSensitive(x, s, t)

    self.assertEquals(jl.concretize(True, y.return_sum()), 11)
    self.assertEquals(jl.concretize(False, y.return_sum()), 1100)

    y.add_a_to_b()
    self.assertEquals(jl.concretize(True, s.a), 1)
    self.assertEquals(jl.concretize(True, s.b), 11)
    self.assertEquals(jl.concretize(True, t.a), 100)
    self.assertEquals(jl.concretize(True, t.b), 1000)
    self.assertEquals(jl.concretize(True, y.a), 1)
    self.assertEquals(jl.concretize(True, y.b), 11)
    self.assertEquals(jl.concretize(False, s.a), 1)
    self.assertEquals(jl.concretize(False, s.b), 10)
    self.assertEquals(jl.concretize(False, t.a), 100)
    self.assertEquals(jl.concretize(False, t.b), 1100)
    self.assertEquals(jl.concretize(False, y.a), 100)
    self.assertEquals(jl.concretize(False, y.b), 1100)

  def test_objects_eq_is(self):
    class TestClass:
      def __init__(self, a):
        self.a = a
    class TestClassEq:
      def __init__(self, a):
        self.a = a
      def __eq__(self, other):
        return self.a == other.a
      def __ne__(self, other):
        return self.a != other.a
      def __lt__(self, other):
        return self.a < other.a
      def __gt__(self, other):
        return self.a > other.a
      def __le__(self, other):
        return self.a <= other.a
      def __ge__(self, other):
        return self.a >= other.a

    jl = JeevesLib
    x = jl.mkLabel('x')
    jl.restrict(x, lambda ctxt : ctxt)

    a = TestClass(3)
    b = TestClass(3)
    c = TestClass(2)

    # Ensure that a < b and b < c (will probably be true anyway,
    # just making sure)
    a, b, c = sorted((a, b, c))
    a.a, b.a, c.a = 3, 3, 2

    v1 = jl.mkSensitive(x, a, c)
    v2 = jl.mkSensitive(x, b, c)
    v3 = jl.mkSensitive(x, c, a)
    self.assertEquals(jl.concretize(True, v1 == v1), True)
    self.assertEquals(jl.concretize(True, v2 == v2), True)
    self.assertEquals(jl.concretize(True, v3 == v3), True)
    self.assertEquals(jl.concretize(True, v1 == v2), False)
    self.assertEquals(jl.concretize(True, v2 == v3), False)
    self.assertEquals(jl.concretize(True, v3 == v1), False)

    self.assertEquals(jl.concretize(True, v1 != v1), False)
    self.assertEquals(jl.concretize(True, v2 != v2), False)
    self.assertEquals(jl.concretize(True, v3 != v3), False)
    self.assertEquals(jl.concretize(True, v1 != v2), True)
    self.assertEquals(jl.concretize(True, v2 != v3), True)
    self.assertEquals(jl.concretize(True, v3 != v1), True)

    self.assertEquals(jl.concretize(True, v1 < v1), False)
    self.assertEquals(jl.concretize(True, v2 < v2), False)
    self.assertEquals(jl.concretize(True, v3 < v3), False)
    self.assertEquals(jl.concretize(True, v1 < v2), True)
    self.assertEquals(jl.concretize(True, v2 < v3), True)
    self.assertEquals(jl.concretize(True, v3 < v1), False)

    self.assertEquals(jl.concretize(True, v1 > v1), False)
    self.assertEquals(jl.concretize(True, v2 > v2), False)
    self.assertEquals(jl.concretize(True, v3 > v3), False)
    self.assertEquals(jl.concretize(True, v1 > v2), False)
    self.assertEquals(jl.concretize(True, v2 > v3), False)
    self.assertEquals(jl.concretize(True, v3 > v1), True)

    self.assertEquals(jl.concretize(True, v1 <= v1), True)
    self.assertEquals(jl.concretize(True, v2 <= v2), True)
    self.assertEquals(jl.concretize(True, v3 <= v3), True)
    self.assertEquals(jl.concretize(True, v1 <= v2), True)
    self.assertEquals(jl.concretize(True, v2 <= v3), True)
    self.assertEquals(jl.concretize(True, v3 <= v1), False)

    self.assertEquals(jl.concretize(True, v1 >= v1), True)
    self.assertEquals(jl.concretize(True, v2 >= v2), True)
    self.assertEquals(jl.concretize(True, v3 >= v3), True)
    self.assertEquals(jl.concretize(True, v1 >= v2), False)
    self.assertEquals(jl.concretize(True, v2 >= v3), False)
    self.assertEquals(jl.concretize(True, v3 >= v1), True)

    self.assertEquals(jl.concretize(False, v2 == v3), False)
    self.assertEquals(jl.concretize(False, v2 != v3), True)
    self.assertEquals(jl.concretize(False, v2 < v3), False)
    self.assertEquals(jl.concretize(False, v2 > v3), True)
    self.assertEquals(jl.concretize(False, v2 <= v3), False)
    self.assertEquals(jl.concretize(False, v2 >= v3), True)

    a = TestClassEq(3)
    b = TestClassEq(3)
    c = TestClassEq(2)

    v1 = jl.mkSensitive(x, a, c)
    v2 = jl.mkSensitive(x, b, c)
    v3 = jl.mkSensitive(x, c, a)
    self.assertEquals(jl.concretize(True, v1 == v1), True)
    self.assertEquals(jl.concretize(True, v2 == v2), True)
    self.assertEquals(jl.concretize(True, v3 == v3), True)
    self.assertEquals(jl.concretize(True, v1 == v2), True)
    self.assertEquals(jl.concretize(True, v2 == v3), False)
    self.assertEquals(jl.concretize(True, v3 == v1), False)

    self.assertEquals(jl.concretize(True, v1 != v1), False)
    self.assertEquals(jl.concretize(True, v2 != v2), False)
    self.assertEquals(jl.concretize(True, v3 != v3), False)
    self.assertEquals(jl.concretize(True, v1 != v2), False)
    self.assertEquals(jl.concretize(True, v2 != v3), True)
    self.assertEquals(jl.concretize(True, v3 != v1), True)

    self.assertEquals(jl.concretize(True, v1 < v1), False)
    self.assertEquals(jl.concretize(True, v2 < v2), False)
    self.assertEquals(jl.concretize(True, v3 < v3), False)
    self.assertEquals(jl.concretize(True, v1 < v2), False)
    self.assertEquals(jl.concretize(True, v2 < v3), False)
    self.assertEquals(jl.concretize(True, v3 < v1), True)

    self.assertEquals(jl.concretize(True, v1 > v1), False)
    self.assertEquals(jl.concretize(True, v2 > v2), False)
    self.assertEquals(jl.concretize(True, v3 > v3), False)
    self.assertEquals(jl.concretize(True, v1 > v2), False)
    self.assertEquals(jl.concretize(True, v2 > v3), True)
    self.assertEquals(jl.concretize(True, v3 > v1), False)

    self.assertEquals(jl.concretize(True, v1 <= v1), True)
    self.assertEquals(jl.concretize(True, v2 <= v2), True)
    self.assertEquals(jl.concretize(True, v3 <= v3), True)
    self.assertEquals(jl.concretize(True, v1 <= v2), True)
    self.assertEquals(jl.concretize(True, v2 <= v3), False)
    self.assertEquals(jl.concretize(True, v3 <= v1), True)

    self.assertEquals(jl.concretize(True, v1 >= v1), True)
    self.assertEquals(jl.concretize(True, v2 >= v2), True)
    self.assertEquals(jl.concretize(True, v3 >= v3), True)
    self.assertEquals(jl.concretize(True, v1 >= v2), True)
    self.assertEquals(jl.concretize(True, v2 >= v3), True)
    self.assertEquals(jl.concretize(True, v3 >= v1), False)

    self.assertEquals(jl.concretize(False, v2 == v3), False)
    self.assertEquals(jl.concretize(False, v2 != v3), True)
    self.assertEquals(jl.concretize(False, v2 < v3), True)
    self.assertEquals(jl.concretize(False, v2 > v3), False)
    self.assertEquals(jl.concretize(False, v2 <= v3), True)
    self.assertEquals(jl.concretize(False, v2 >= v3), False)

  def test_objects_operators(self):
    return NotImplemented

  def test_objects_delattr(self):
    return NotImplemented

  def test_objects_hasattr(self):
    return NotImplemented

  def test_objects_callable(self):
    return NotImplemented

  def test_functions_operators(self):
    return NotImplemented

  def test_accessing_special_attributes(self):
    return NotImplemented

  def test_attribute_names(self):
    return NotImplemented

  def test_jhasElt(self):
    jl = JeevesLib

    a = jl.mkLabel ()
    jl.restrict(a, lambda x: x)
    xS = jl.mkSensitive(a, 42, 1)

    b = jl.mkLabel ()
    jl.restrict(b, lambda x: x)
    yS = jl.mkSensitive(b, 43, 3)

    lst = [xS, 2, yS]
    self.assertEquals(jl.concretize(True, jl.jhasElt(lst, lambda x: x == 42))
        , True)
    self.assertEquals(jl.concretize(False, jl.jhasElt(lst, lambda x: x == 42))
        , False)
    self.assertEquals(jl.concretize(True, jl.jhasElt(lst, lambda x: x == 1))
        , False)
    self.assertEquals(jl.concretize(False, jl.jhasElt(lst, lambda x: x == 1))
        , True)
    self.assertEquals(jl.concretize(True, jl.jhasElt(lst, lambda x: x == 43))
        , True)
    self.assertEquals(jl.concretize(False, jl.jhasElt(lst, lambda x: x == 43))
        , False)
    self.assertEquals(jl.concretize(True, jl.jhasElt(lst, lambda x: x == 3))
        , False)
    self.assertEquals(jl.concretize(False, jl.jhasElt(lst, lambda x: x == 3))
        , True)


if __name__ == '__main__':
    unittest.main()
