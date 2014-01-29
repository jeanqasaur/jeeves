'''
This tests code after the macro transformation.
'''
import JeevesLib
from smt.Z3 import *
import sys
import unittest

class User:
  def __init__(self, userId):
    self.userId = userId

class GPS:
  def __init__(self, lt, lg):
    self.lt = lt
    self.lg = lg
  def distance(self, other):
    return abs(self.lt - other.lt) + abs(self.lg - other.lg)
  def __eq__(self, other):
    return (self.lt == other.lt) and (self.lg == other.lg)

class LocationContext:
  def __init__(self, user, location):
    self.user = user
    self.location = location 

class TestJeevesBasic(unittest.TestCase):
  def setUp(self):
    self.s = Z3()
    # reset the Jeeves state
    JeevesLib.init()

  '''
  Basic example of showing different values to different viewers.
  '''
  def testBasic(self):
    alice = User(0)
    bob = User(1)

    a = JeevesLib.mkLabel()
    JeevesLib.restrict(a, lambda oc: oc == alice)
    xS = JeevesLib.mkSensitive(a, 42, 0)
    self.assertEqual(42, JeevesLib.concretize(alice, xS))
    self.assertEqual(0, JeevesLib.concretize(bob, xS))

  '''
  Using 'and' and 'or'. Without the source transformation, we have to use 'jand'
  and 'jor' explicitly because of the lack of overloading.
  '''
  def testAndOr(self):
    alice = User(0)
    bob = User(1)
    charlie = User(2)

    a = JeevesLib.mkLabel()
    JeevesLib.restrict(a
        , lambda oc: JeevesLib.jor(lambda: oc == alice, lambda: oc == bob))
    xS = JeevesLib.mkSensitive(a, 42, 0)
    self.assertEqual(42, JeevesLib.concretize(alice, xS))
    self.assertEqual(42, JeevesLib.concretize(bob, xS))
    self.assertEqual(0, JeevesLib.concretize(charlie, xS))

  '''
  Example of using dynamic state in a policy.
  '''
  def testStatefulPolicy(self):
    alice = User(0)
    bob = User(1)
    charlie = User(2)

    friends = { alice: [bob], bob: [alice], charlie: [] }
    a = JeevesLib.mkLabel()
    # Policy: can see if viewer is in the friends list.
    JeevesLib.restrict(a
        , lambda oc: JeevesLib.jhas(friends[alice], oc))
    xS = JeevesLib.mkSensitive(a, 42, 0)
    # Bob can see but Alice and Charlie can not.
    self.assertEqual(0, JeevesLib.concretize(alice, xS))
    self.assertEqual(42, JeevesLib.concretize(bob, xS))
    self.assertEqual(0, JeevesLib.concretize(charlie, xS))

    # Update friends list and now Charlie can see.
    friends[alice].append(charlie)
    
    self.assertEqual(0, JeevesLib.concretize(alice, xS))
    self.assertEqual(42, JeevesLib.concretize(bob, xS))
    self.assertEqual(42, JeevesLib.concretize(charlie, xS))

  '''
  Example of a policy that depends on a sensitive value.
  '''
  def testDependentPolicy(self):
    defaultLoc = GPS(sys.maxint, sys.maxint)
    
    alice = User(0)
    a = JeevesLib.mkLabel()
    aliceLoc = JeevesLib.mkSensitive(a, GPS(0, 0), defaultLoc)
    JeevesLib.restrict(a, lambda oc: oc.location.distance(aliceLoc) < 25)
    aliceCtxt = LocationContext(alice, aliceLoc)

    bob = User(1)
    self.assertEqual(GPS(0, 0)
        , JeevesLib.concretize(LocationContext(bob, GPS(5, 5)), aliceLoc))
    self.assertEqual(defaultLoc
        , JeevesLib.concretize(LocationContext(bob, GPS(12, 13)), aliceLoc))

  '''
  Example with a circular dependency.
  '''
  def testCircularDependency(self):
    a = JeevesLib.mkLabel()
    alice = User(0)
    bob = User(1)
    charlie = User(2)
    guestList = JeevesLib.JList([alice, bob])
    guestListS = JeevesLib.mkSensitive(a, guestList, JeevesLib.JList([]))
    JeevesLib.restrict(a, lambda oc: JeevesLib.jhas(guestListS, oc))

    self.assertEqual(guestList, JeevesLib.concretize(alice, guestListS))
    self.assertEqual(guestList, JeevesLib.concretize(bob, guestListS))
    self.assertEqual([], JeevesLib.concretize(charlie, guestListS).l)

  '''
  Conditionals.
  '''
  def testConditional(self):
    a = JeevesLib.mkLabel()
    alice = User(0) 
    bob = User(1)
    JeevesLib.restrict(a, lambda oc: oc == alice)
    xS = JeevesLib.mkSensitive(a, 42, 0)
    r = JeevesLib.jif(xS == 42, lambda: 1, lambda: 2)
    self.assertEqual(1, JeevesLib.concretize(alice, r))
    self.assertEqual(2, JeevesLib.concretize(bob, r))

  '''
  Functions.
  '''
  def testFunction(self):
    pass

if __name__ == '__main__':
    unittest.main()
