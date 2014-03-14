import JeevesLib
import unittest

from fast.ProtectedRef import ProtectedRef, UpdateResult
from sourcetrans.macro_module import macros, jeeves

class User:
  def __init__(self, userId):
    self.userId = userId

# Test that once values are sanitized, they may flow to the output, but not
# before.
class TestFunctions(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    self.alice = User(0)
    self.bob = User(1)

  # If the input does not do anything bad to our data structure, then we
  # allow it to pass.
  @jeeves
  def testBehavioralGood(self):
    touchedBadData = False
    def f(x):
      return x+1
    x = ProtectedRef(lambda x: x, None
      , lambda _this: lambda ic: lambda touchedBad: not touchedBad)
    self.assertEqual(JeevesLib.concretize(None, (x.v)(1)), 1)
    assert x.update(None, None, f) == UpdateResult.Unknown
    self.assertEqual(JeevesLib.concretize(None, (x.v)(1)), 2)

  @jeeves
  def testBehavioralBad(self):
    touchedBadData = False
    def f(x):
      global touchedBadData
      touchedBadData = True
      return x+1
    x = ProtectedRef(lambda x: x, None
      , lambda _this: lambda ic: lambda oc: not touchedBadData)
    self.assertEqual(JeevesLib.concretize(None, (x.v)(1)), 1)
    assert x.update(None, None, f) == UpdateResult.Unknown
    self.assertEqual(JeevesLib.concretize(None, (x.v)(1)), 1)

  # TODO: Users can endorse functions.

if __name__ == '__main__':
    unittest.main()
