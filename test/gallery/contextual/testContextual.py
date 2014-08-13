import unittest

from sourcetrans.macro_module import macros, jeeves
import JeevesLib

class Location:
  class Home:
    pass
  class Work:
    pass
  class Other:
    pass

class User:
  def __init__(self, userId):
    self.userId = userId

class Context:
  def __init__(self, user, location):
    self.user = user
    self.location = location

class TestContextual(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    self.alice = User(0)
    self.bob = User(1)

  @jeeves
  def testContextual(self):
    a = JeevesLib.mkLabel()
    JeevesLib.restrict(a
      , lambda oc: oc.user == self.alice or oc.location == Location.Work)
    xS = JeevesLib.mkSensitive(a, 42, 0)
    self.assertEqual(
        JeevesLib.concretize(Context(self.alice, Location.Work), xS)
      , 42)
    self.assertEqual(
        JeevesLib.concretize(Context(self.alice, Location.Home), xS)
      , 42)
    self.assertEqual(
        JeevesLib.concretize(Context(self.bob, Location.Work), xS)
      , 42)
    self.assertEqual(
        JeevesLib.concretize(Context(self.bob, Location.Home), xS)
      , 0)

if __name__ == '__main__':
    unittest.main()
