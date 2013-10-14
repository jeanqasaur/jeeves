import unittest
import macropy.activate

import JeevesLib
from fast.AST import *
from eval.Eval import partialEval
from env.PathVars import PositiveVariable, NegativeVariable

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

        self.assertEqual(r.eval({}), ((((20 + 1) - 2) * 3) / 3) % 5)

    def testArithmeticR(self):
        t = Constant(20)
        r = 40000 % (1000 / (3 * (2 - (1 + t))))
        self.assertEqual(r.left.v, 40000)
        self.assertEqual(r.right.left.v, 1000)
        self.assertEqual(r.right.right.left.v, 3)
        self.assertEqual(r.right.right.right.left.v, 2)
        self.assertEqual(r.right.right.right.right.left.v, 1)
        self.assertEqual(r.right.right.right.right.right.v, 20)

        self.assertEqual(r.eval({}), 40000 % (1000 / (3 * (2 - (1 + 20)))))

    def testBooleans(self):
        for a in (True, False):
            r = Not(Constant(a))
            self.assertEqual(r.sub.v, a)
            self.assertEqual(r.eval({}), not a)

            for b in (True, False):
                r = Or(Constant(a), Constant(b))
                self.assertEqual(r.left.v, a)
                self.assertEqual(r.right.v, b)
                self.assertEquals(r.eval({}), a or b)

                r = And(Constant(a), Constant(b))
                self.assertEqual(r.left.v, a)
                self.assertEqual(r.right.v, b)
                self.assertEquals(r.eval({}), a and b)

                r = Implies(Constant(a), Constant(b))
                self.assertEqual(r.left.v, a)
                self.assertEqual(r.right.v, b)
                self.assertEquals(r.eval({}), (not a) or b)

    def testComparisons(self):
        a = Constant(20)
        
        b = a == 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = a != 40
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)
        self.assertEqual(b.eval({}), True)

        b = a > 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = a >= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = a < 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), True)

        b = a <= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), True)
 
        b = 40 == a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = 40 != a
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)
        self.assertEqual(b.eval({}), True)

        b = 40 > a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), True)

        b = 40 >= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), True)

        b = 40 < a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = 40 <= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
        self.assertEqual(b.eval({}), False)

        b = a == 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)

        b = a != 20
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = a > 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = a >= 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)

        b = a < 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = a <= 20
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)
 
        b = 20 == a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)

        b = 20 != a
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = 20 > a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = 20 >= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)

        b = 20 < a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), False)

        b = 20 <= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 20)
        self.assertEqual(b.eval({}), True)

    def testPartialEval(self):
        JeevesLib.init()

        l = Var("l")

        a = Facet(l, Constant(1), Constant(2))
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        self.assertEqual(ap.eval({l:True}), 1)
        self.assertEqual(ap.eval({l:False}), 2)

        a = Facet(l, Add(Constant(1), Constant(-1)), Constant(2))
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        self.assertEqual(ap.eval({l:True}), 0)
        self.assertEqual(ap.eval({l:False}), 2)

        a = Add(
            Facet(l, Constant(1), Constant(10)),
            Facet(l, Constant(100), Constant(1000))
        )
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        self.assertEqual(ap.eval({l:True}), 101)
        self.assertEqual(ap.eval({l:False}), 1010)

        l1 = Var("l1")
        l2 = Var("l2")
        a = Add(
            Facet(l1, Constant(1), Constant(10)),
            Facet(l2, Constant(100), Constant(1000))
        )
        ap = partialEval(a)
        self.assertTrue(isPureFacetTree(ap))
        self.assertEqual(ap.eval({l1:True, l2:True}), 101)
        self.assertEqual(ap.eval({l1:True, l2:False}), 1001)
        self.assertEqual(ap.eval({l1:False, l2:True}), 110)
        self.assertEqual(ap.eval({l1:False, l2:False}), 1010)
