import JeevesLib
from smt.Z3 import *
import unittest
from Location import Location, GPS, City, Country, User
import JeevesLib

class TestLocation(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    # Define some locations.
    self.countryUSA = Country("USA")
    self.cityCambridge = City("Cambridge", self.countryUSA)
    self.gpsMIT = GPS(40.589063, -74.159178, self.cityCambridge) 

    # Define some users.
    # TODO: Make some faceted location values.
    self.alice = User(0, self.cityCambridge)
    self.bob = User(1, self.cityCambridge)
    self.carol = User(2, self.countryUSA)

    self.alice.addFriend(self.bob)
    self.bob.addFriend(self.alice)

  def testIsin(self):
    self.assertTrue(self.cityCambridge.isIn(self.cityCambridge))
    self.assertTrue(self.cityCambridge.isIn(self.countryUSA))
    self.assertTrue(self.gpsMIT.isIn(self.gpsMIT))
    self.assertTrue(self.gpsMIT.isIn(self.countryUSA))
    self.assertFalse(self.cityCambridge.isIn(self.gpsMIT))
    self.assertFalse(self.countryUSA.isIn(self.gpsMIT))
    self.assertFalse(self.countryUSA.isIn(self.cityCambridge))

  def testIsFriends(self):
    self.assertTrue(
      JeevesLib.concretize(self.alice, self.alice.isFriends(self.bob)))
    self.assertTrue(
      JeevesLib.concretize(self.alice, self.bob.isFriends(self.alice)))
    self.assertFalse(
      JeevesLib.concretize(self.alice, self.alice.isFriends(self.carol)))
    self.assertFalse(
      JeevesLib.concretize(self.alice, self.carol.isFriends(self.alice)))

'''
    lab = JeevesLib.mkLabel ()
    # TODO: Add policy that the output channel has to be either the owner or
    # satisfy the policy on it (policy(oc)).
    JeevesLib.restrict(lab
        , lambda oc: JeevesLib.jor(
            lambda: oc.user == owner, lambda: policy(oc)))
    '''


if __name__ == '__main__':
    unittest.main()
