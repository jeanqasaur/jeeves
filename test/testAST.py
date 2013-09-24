import unittest
import macropy.activate

from fast.AST import *
from eval.Eval import partialEval
from env.PathVars import PositiveVariable, NegativeVariable
import JeevesLib, JeevesGlobal

def isPureFacetTree(f):
    if isinstance(f, Constant):
        return True
    elif isinstance(f, Facet):
        return isPureFacetTree(f.thn) and isPureFacetTree(f.els)
    else:
        return False


class TestAST(unittest.TestCase):

    def setUp(self):
        pass

    # TODO test eval

    def testArithmeticL(self):
        t = Constant(20)
        r = ((((t + 1) - 2) * 3) / 3) % 5
        self.assertEqual(r.right.v, 5)
        self.assertEqual(r.left.right.v, 3)
        self.assertEqual(r.left.left.right.v, 3)
        self.assertEqual(r.left.left.left.right.v, 2)
        self.assertEqual(r.left.left.left.left.right.v, 1)
        self.assertEqual(r.left.left.left.left.left.v, 20)

        self.assertEqual(r.eval(), ((((20 + 1) - 2) * 3) / 3) % 5)

    def testArithmeticR(self):
        t = Constant(20)
        r = 40000 % (1000 / (3 * (2 - (1 + t))))
        self.assertEqual(r.left.v, 40000)
        self.assertEqual(r.right.left.v, 1000)
        self.assertEqual(r.right.right.left.v, 3)
        self.assertEqual(r.right.right.right.left.v, 2)
        self.assertEqual(r.right.right.right.right.left.v, 1)
        self.assertEqual(r.right.right.right.right.right.v, 20)

        self.assertEqual(r.eval(), 40000 % (1000 / (3 * (2 - (1 + 20)))))

    def testComparisons(self):
        a = Constant(20)
        
        b = a == 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = a != 40
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)
        self.assertEqual(b.eval(), True)

        b = a > 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = a >= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = a < 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), True)

        b = a <= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), True)
 
        b = 40 == a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = 40 != a
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)
        self.assertEqual(b.eval(), True)

        b = 40 > a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), True)

        b = 40 >= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), True)

        b = 40 < a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = 40 <= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval(), False)

        b = a == 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)

        b = a != 20
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = a > 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = a >= 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)

        b = a < 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = a <= 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)
 
        b = 20 == a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)

        b = 20 != a
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = 20 > a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = 20 >= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)

        b = 20 < a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), False)

        b = 20 <= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval(), True)

    def testPartialEval(self):
        jl = JeevesLib.JeevesLib()
        JeevesGlobal.set_jeeves_state(jl)

        l = Var("l")

        a = Facet(l, Constant(1), Constant(2))
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        with PositiveVariable(l):
            self.assertEqual(a.eval(), 1)
        with NegativeVariable(l):
            self.assertEqual(a.eval(), 2)

        a = Facet(l, Add(Constant(1), Constant(-1)), Constant(2))
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        with PositiveVariable(l):
            self.assertEqual(ap.eval(), 0)
        with NegativeVariable(l):
            self.assertEqual(ap.eval(), 2)

        a = Add(
            Facet(l, Constant(1), Constant(10)),
            Facet(l, Constant(100), Constant(1000))
        )
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        with PositiveVariable(l):
            self.assertEqual(ap.eval(), 101)
        with NegativeVariable(l):
            self.assertEqual(ap.eval(), 1010)

        l1 = Var("l1")
        l2 = Var("l2")
        a = Add(
            Facet(l1, Constant(1), Constant(10)),
            Facet(l2, Constant(100), Constant(1000))
        )
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        with PositiveVariable(l1):
            with PositiveVariable(l2):
                self.assertEqual(ap.eval(), 101)
            with NegativeVariable(l2):
                self.assertEqual(ap.eval(), 1001)
        with NegativeVariable(l1):
            with PositiveVariable(l2):
                self.assertEqual(ap.eval(), 110)
            with NegativeVariable(l2):
                self.assertEqual(ap.eval(), 1010)
