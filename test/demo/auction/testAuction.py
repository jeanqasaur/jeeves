import macropy.activate
from smt.Z3 import *
import unittest
from demo.auction.Auction import User
import JeevesGlobal
import JeevesLib

class TestAuthConfidentiality(unittest.TestCase):
  def setUp(self):
    JeevesGlobal.set_jeeves_state(JeevesLib.JeevesLib())

  def testUserCannotSeeOtherPassword(self):
    pass

  def testSensitiveUserPassword(self):
    # Make a sensitive user that is either Alice or Bob. Make sure it shows the
    # the right password based on the access level of the user.
    pass

if __name__ == '__main__':
    unittest.main()
