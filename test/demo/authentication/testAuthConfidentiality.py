import macropy.activate
from smt.Z3 import *
import unittest
from demo.authentication.AuthConfidentiality import User
import JeevesGlobal
import JeevesLib

class TestAuthConfidentiality(unittest.TestCase):
  def setUp(self):
    JeevesGlobal.set_jeeves_state(JeevesLib.JeevesLib())
    self.alicePwd = "alicePwd"
    self.bobPwd = "bobPwd"
    self.aliceUser = User(1, "Alice", self.alicePwd)
    self.bobUser = User(2, "Bob", self.bobPwd)

  def testUserCanSeeOwnPassword(self):  
    alicePwdToAlice = JeevesGlobal.jeevesLib.concretize(
        self.aliceUser.getPwd(), self.aliceUser)
    assertEquals(alicePwdToAlice, self.alicePwd)

  def testUserCannotSeeOtherPassword(self):
    bobPwdToAlice = JeevesGlobal.jeevesLib.concretize(
        self.bobUser.getPwd(), self.aliceUser)
    assertEquals(bobPwdToAlice, "")

  def testSensitiveUserPassword(self):
    # Make a sensitive user that is either Alice or Bob. Make sure it shows the
    # the right password based on the access level of the user.
    pass

if __name__ == '__main__':
    unittest.main()
