import macropy.activate
from smt.Z3 import *
import unittest
from demo.auction.Auction import AuctionContext, Bid, User
import JeevesGlobal
import JeevesLib

class TestAuction(unittest.TestCase):
  def setUp(self):
    JeevesGlobal.set_jeeves_state(JeevesLib.JeevesLib())
    self.aliceUser = User(0)
    self.bobUser = User(1)
    self.claireUser = User(2)

  def testOwnerCanSee(self):
    policy = lambda oc: False
    aliceBid = Bid(3, self.aliceUser, policy)
    
    ctxt0 = AuctionContext(self.aliceUser, 0, [])
    self.assertEqual(3
        , JeevesGlobal.jeevesLib.concretize(ctxt0, aliceBid.value))

    ctxt1 = AuctionContext(self.bobUser, 0, [])
    self.assertEqual(-1
        , JeevesGlobal.jeevesLib.concretize(ctxt1, aliceBid.value))

  def testTimeSensitiveRelease(self):
    auctionEndTime = 10
    policy = lambda oc: oc.time > auctionEndTime
    aliceBid = Bid(3, self.aliceUser, policy)

    self.assertEqual(3
        , JeevesGlobal.jeevesLib.concretize(
          AuctionContext(self.bobUser, 11, []), aliceBid.value))
    self.assertEqual(-1
        , JeevesGlobal.jeevesLib.concretize(
          AuctionContext(self.bobUser, 10, []), aliceBid.value))

  def testSealedAuction(self):
    def hasBidFromUser(ctxt, u):
      # TODO: Be able to support something along the lines of
      #   ctxt.
      # where things can be faceted values.
      return NotImplemented
    allUsers = [self.aliceUser, self.bobUser, self.claireUser]
    policy = lambda oc: NotImplemented
    # need to wait for jand for this...
    # lambda oc: reduce(lambda acc, c) => hasBidFromUser(occ, c) && acc

    aliceBid = Bid(3, self.aliceUser, policy)
    bobBid = Bid(4, self.bobUser, policy)
    claireBid = Bid(5, self.claireUser, policy)

    self.assertEqual(-1,
      JeevesGlobal.jeevesLib.concretize(
        AuctionContext(self.bobUser, 11, [aliceBid]), aliceBid.value))

if __name__ == '__main__':
    unittest.main()
