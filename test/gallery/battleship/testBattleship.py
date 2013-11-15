import macropy.activate
import JeevesLib
from smt.Z3 import *
import unittest
import Battleship
import JeevesLib

class TestBattleship(unittest.TestCase):
  def setUp(self):
    JeevesLib.init()

  '''
  def testOwnerCanSee(self):
    policy = lambda oc: False
    aliceBid = Bid(3, self.aliceUser, policy)
    
    ctxt0 = AuctionContext(self.aliceUser, 0, [])
    self.assertEqual(3
        , JeevesLib.concretize(ctxt0, aliceBid.value))

  '''

if __name__ == '__main__':
    unittest.main()
