import JeevesLib
import unittest
import Auth

class TestHealthWeb(unittest.TestCase):
  def setUp(self):
    JeevesLib.init()
    # x = Auth.Test()
    # self.auth = Authentication()
    self.alicePrin = Auth.U("Alice")
    self.adminPrin = Auth.Admin()

  '''
  Test Auth.
  '''
  def testEqualities(self):
    self.assertEqual(Auth.U("Alice"), Auth.U("Alice"))
    self.assertEqual(Auth.MkCred(self.alicePrin), Auth.MkCred(self.alicePrin))
    self.assertEqual(Auth.Admin(), Auth.Admin())
    self.assertNotEqual(Auth.U("Alice"), Auth.Admin())

  def testLogin(self):
    self.assertEqual(
      self.alicePrin.login("AlicePW"), Auth.MkCred(self.alicePrin))
    self.assertEqual(self.alicePrin.login("xyz"), None)
    self.assertEqual(self.adminPrin.login("AdminPW"), Auth.MkCred(self.adminPrin))

  
