import JeevesLib
from smt.Z3 import *
import unittest
from Location import Location, GPS, City, Country, User, LocationNetwork
import JeevesLib

class TestLocation(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    # Define some locations.
    self.countryUSA = Country("USA")
    self.cityCambridge = City("Cambridge", self.countryUSA)
    self.gpsMIT = GPS(40.589063, -74.159178, self.cityCambridge) 

    # Define some users with their locations.
    # Alice's location is restricted to Alice and her friends.
    aliceLabel = JeevesLib.mkLabel()
    JeevesLib.restrict(aliceLabel
      , lambda oc: owner == oc or owner.isFriends(oc))
    self.alice = User(0
      , JeevesLib.mkSensitive(aliceLabel, self.gpsMIT, self.cityCambridge))
    
    # Bob's location has no policies.
    self.bob = User(1, self.cityCambridge)

    
    self.carol = User(2, self.countryUSA)

    self.alice.addFriend(self.bob)
    self.bob.addFriend(self.alice)

  # This makes sure the isIn function works properly.
  def testIsin(self):
    self.assertTrue(self.cityCambridge.isIn(self.cityCambridge))
    self.assertTrue(self.cityCambridge.isIn(self.countryUSA))
    self.assertTrue(self.gpsMIT.isIn(self.gpsMIT))
    self.assertTrue(self.gpsMIT.isIn(self.countryUSA))
    self.assertFalse(self.cityCambridge.isIn(self.gpsMIT))
    self.assertFalse(self.countryUSA.isIn(self.gpsMIT))
    self.assertFalse(self.countryUSA.isIn(self.cityCambridge))

  # This makes sure the isFriends function works properly.
  def testIsFriends(self):
    self.assertTrue(
      JeevesLib.concretize(self.alice, self.alice.isFriends(self.bob)))
    self.assertTrue(
      JeevesLib.concretize(self.alice, self.bob.isFriends(self.alice)))
    self.assertFalse(
      JeevesLib.concretize(self.alice, self.alice.isFriends(self.carol)))
    self.assertFalse(
      JeevesLib.concretize(self.alice, self.carol.isFriends(self.alice)))

  # This makes sure locations can only be viewed if they are supposed to be
  # viewed.
  def testViewLocation(self):
    # Alice and Bob can see the high-confidentiality version of Alice's
    # location, but Carol cannot.
    self.assertEqual(JeevesLib.concretize(self.alice, self.alice.location)
      , self.gpsMIT)
    self.assertEqual(JeevesLib.concretize(self.bob, self.alice.location)
      , self.gpsMIT)
    self.assertEqual(JeevesLib.concretize(self.carol, self.alice.location)
      , self.cityCambridge)

  def testCountUsersInLocation(self):
    # Only Alice and Bob can see Alice's "high" location of S
    locNetwork = LocationNetwork([self.alice, self.bob, self.carol])
    usersInStata = locNetwork.countUsersInLocation(self.gpsMIT)
    self.assertEqual(JeevesLib.concretize(self.alice, usersInStata), 1)
    self.assertEqual(JeevesLib.concretize(self.bob, usersInStata), 1)
    self.assertEqual(JeevesLib.concretize(self.carol, usersInStata), 0)

if __name__ == '__main__':
    unittest.main()
