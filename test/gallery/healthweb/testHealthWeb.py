import JeevesLib
import unittest
from Auth import Authentication

class TestHealthWeb(unittest.TestCase):
  def setUp(self):
    JeevesLib.init()
    self.auth = Authentication()
    # self.alicePrin = Authentication.Prin.U("Alice")
    # self.adminPrin = Authentication.Prin.Admin

  def testLogin(self):
    pass
    # self.assertEqual(self.auth.login(self.alicePrin, "AlicePW"), Cred.MkCred(self.alicePrin))
