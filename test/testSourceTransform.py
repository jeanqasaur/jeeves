import unittest
import macropy.activate
from sourcetrans.macro_module import macros, jeeves
import JeevesLib

class TestSourceTransform(unittest.TestCase):
  def setUp(self):
    # reset the Jeeves state
    JeevesLib.init()

  @jeeves
  def test_basic(self):
    x = JeevesLib.mkLabel('x')
    JeevesLib.restrict(x, lambda _: True)
    xConcrete = JeevesLib.concretize(None, x)
    self.assertTrue(xConcrete)
