from smt.Z3 import *
import unittest

from fast.ProtectedRef import ProtectedRef, UpdateResult
from Location import Location, GPS, City, Country, User, LocationNetwork
import JeevesLib
from sourcetrans.macro_module import macros, jeeves

class TestLocationFlow(unittest.TestCase):
  def setUp(self):
    def canSee(owner, ctxt):
      return owner == ctxt or owner.isFriends(ctxt)

    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    # Define some locations.
    self.countryUSA = Country("USA")
    self.cityCambridge = City("Cambridge", self.countryUSA)
    self.gpsMIT = GPS(40.589063, -74.159178, self.cityCambridge) 

    # Define some users.
    self.alice = User(0)
#      , JeevesLib.mkSensitive(aliceLabel, self.gpsMIT, self.cityCambridge))
    self.bob = User(1) #, self.cityCambridge)
    self.carol = User(2) #, self.countryUSA)

    self.alice.addFriend(self.bob)
    self.bob.addFriend(self.alice)

    aliceLabel = JeevesLib.mkLabel()
    JeevesLib.restrict(aliceLabel, lambda oc: oc == self.alice or self.alice.isFriends(oc))
    self.aliceLoc = JeevesLib.mkSensitive(aliceLabel, self.gpsMIT
                      , self.cityCambridge)

  @jeeves
  def testUpdates(self):
    # Bob cannot update Alice's location.
    self.assertEqual(
      self.alice.location.update(self.bob, self.bob, self.aliceLoc)
      , UpdateResult.Unknown)

    # Alice updates her location.
    self.assertEqual(self.alice.location.update(self.alice, self.alice
      , self.aliceLoc), UpdateResult.Unknown)
    # Only Alice and her friends can see the high-confidentiality version of
    # her location.
    self.assertEqual(JeevesLib.concretize(self.alice, self.alice.location.v)
      , self.gpsMIT)
    self.assertEqual(JeevesLib.concretize(self.bob, self.alice.location.v)
      , self.gpsMIT)
    # TODO: This doesn't work yet because we don't have a rank-ordering of
    # labels associated with write policies so that we can prioritize assigning
    # certain labels to high over others.
    self.assertEqual(JeevesLib.concretize(self.carol, self.alice.location.v)
      , self.cityCambridge)

  def testCountUsersInLocation(self):
    self.assertEqual(self.alice.location.update(self.alice, self.alice
      , self.aliceLoc), UpdateResult.Unknown)
    self.assertEqual(self.bob.location.update(self.bob, self.bob, self.cityCambridge), UpdateResult.Unknown)
    self.assertEqual(self.carol.location.update(self.carol, self.carol, self.countryUSA), UpdateResult.Unknown)

    # Only Alice and Bob can see Alice's "high" location of S
    locNetwork = LocationNetwork([self.alice, self.bob, self.carol])
    usersInStata = locNetwork.countUsersInLocation(self.gpsMIT)
    self.assertEqual(JeevesLib.concretize(self.alice, usersInStata), 1)
    self.assertEqual(JeevesLib.concretize(self.bob, usersInStata), 1)
    self.assertEqual(JeevesLib.concretize(self.carol, usersInStata), 0)

if __name__ == '__main__':
    unittest.main()
