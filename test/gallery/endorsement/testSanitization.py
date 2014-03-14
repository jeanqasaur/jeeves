import JeevesLib
import unittest

from fast.ProtectedRef import ProtectedRef, UpdateResult
import JeevesLib
from sourcetrans.macro_module import macros, jeeves

class User:
  def __init__(self, userId):
    self.userId = userId

# Test that once values are sanitized, they may flow to the output, but not
# before.
class TestSanitization(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    self.alice = User(0)
    self.bob = User(1)

  # If the input does not do anything bad to our data structure, then we
  # allow it to pass.
  @jeeves
  def testBehavioralSanitizationGood(self):
    touchedBadData = False
    def f(s):
      global touchedBadData
      if s == "bad":
        touchedBadData = True
      return s
    x = ProtectedRef("dunno", None
      , lambda _this: lambda ic: lambda oc: not touchedBadData)
    self.assertEqual(JeevesLib.concretize(None, x.v), "dunno")
    assert x.update(None, None, f("good")) == UpdateResult.Unknown
    self.assertEqual(JeevesLib.concretize(None, x.v), "good")

  @jeeves
  def testBehavioralSanitizationBad(self):
    touchedBadData = False
    def f(s):
      global touchedBadData
      if s == "bad":
        touchedBadData = True
      return s
    x = ProtectedRef("dunno", None
      , lambda _this: lambda ic: lambda oc: not touchedBadData)
    assert x.update(None, None, f("bad")) == UpdateResult.Unknown
    print touchedBadData
    self.assertEqual(JeevesLib.concretize(None, x.v), "dunno")


  def testEndorseSanitizeFunction(self):
    pass
    # TODO: Need a way of associating sanitization function with some sort of
    # endorsement, probably with facet rewriting.

if __name__ == '__main__':
    unittest.main()
