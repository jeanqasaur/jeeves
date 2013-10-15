import macropy.activate
import JeevesLib
from smt.Z3 import *
import unittest
from Auction import AuctionContext, Bid, User
import JeevesLib

class TestAuction(unittest.TestCase):
  def setUp(self):
    JeevesLib.init()
    self.aliceUser = User(0)
    self.bobUser = User(1)
    self.claireUser = User(2)

  def testOwnerCanSee(self):
    policy = lambda oc: False
    aliceBid = Bid(3, self.aliceUser, policy)
    
    ctxt0 = AuctionContext(self.aliceUser, 0, [])
    self.assertEqual(3
        , JeevesLib.concretize(ctxt0, aliceBid.value))

    ctxt1 = AuctionContext(self.bobUser, 0, [])
    self.assertEqual(-1
        , JeevesLib.concretize(ctxt1, aliceBid.value))

  def testTimeSensitiveRelease(self):
    auctionEndTime = 10
    policy = lambda oc: oc.time > auctionEndTime
    aliceBid = Bid(3, self.aliceUser, policy)

    self.assertEqual(3
        , JeevesLib.concretize(
          AuctionContext(self.bobUser, 11, []), aliceBid.value))
    self.assertEqual(-1
        , JeevesLib.concretize(
          AuctionContext(self.bobUser, 10, []), aliceBid.value))

  def testSealedAuction(self):
    # Function that returns true if the context contains a bid from the given
    # user.
    def hasBidFromUser(ctxt, u):
      return JeevesLib.jhasElt(ctxt.bids, lambda b: b.owner == u)
    allUsers = [self.aliceUser, self.bobUser, self.claireUser]
    policy = lambda oc: reduce(lambda acc, c: JeevesLib.jand(
                    lambda: hasBidFromUser(oc, c), lambda: acc)
                  , allUsers)

    aliceBid = Bid(3, self.aliceUser, policy)
    bobBid = Bid(4, self.bobUser, policy)
    claireBid = Bid(5, self.claireUser, policy)

    self.assertEqual(-1,
      JeevesLib.concretize(
        AuctionContext(self.bobUser, 11, [aliceBid]), aliceBid.value))

if __name__ == '__main__':
    unittest.main()
