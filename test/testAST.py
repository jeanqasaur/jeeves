import unittest

from fast.AST import *

class TestAST(unittest.TestCase):

    def setUp(self):
        pass

    # TODO test eval

    def testArithmeticL(self):
        t = IntVal(20)
        r = ((((t + 1) - 2) * 3) / 3) % 5
        self.assertEqual(r.right.v, 5)
        self.assertEqual(r.left.right.v, 3)
        self.assertEqual(r.left.left.right.v, 3)
        self.assertEqual(r.left.left.left.right.v, 2)
        self.assertEqual(r.left.left.left.left.right.v, 1)
        self.assertEqual(r.left.left.left.left.left.v, 20)

    def testArithmeticR(self):
        t = IntVal(20)
        r = 5 % (3 / (3 * (2 - (1 + t))))
        self.assertEqual(r.left.v, 5)
        self.assertEqual(r.right.left.v, 3)
        self.assertEqual(r.right.right.left.v, 3)
        self.assertEqual(r.right.right.right.left.v, 2)
        self.assertEqual(r.right.right.right.right.left.v, 1)
        self.assertEqual(r.right.right.right.right.right.v, 20)

    def testComparisons(self):
        a = IntVal(20)
        
        b = a == 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = a != 40
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)

        b = a > 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = a >= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = a < 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = a >= 40
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
 
        b = 40 == a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = 40 != a
        self.assertEqual(b.sub.left.v, 20)
        self.assertEqual(b.sub.right.v, 40)

        b = 40 > a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = 40 >= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = 40 < a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)

        b = 40 <= a
        self.assertEqual(b.left.v, 20)
        self.assertEqual(b.right.v, 40)
