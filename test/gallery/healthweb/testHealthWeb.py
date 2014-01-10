import JeevesLib
import unittest
import mock
# from mock import MagicMock
from mock import patch

import Auth
import ExternNetwork
from ExternNetwork import Request, Response
import HealthMgr

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

  '''
  Test that we're mocking things up correctly...
  '''
  def testMockNetwork(self):
    ExternNetwork.request = mock.Mock(return_value=[])
    self.assertEqual(ExternNetwork.request(), [])

    ExternNetwork.respond = mock.Mock()
    ExternNetwork.respond(Response.Ok)
    ExternNetwork.respond.assert_called_with(Response.Ok)

  def testEvlLoop(self):
    pass
