from smt.Z3 import *
import unittest

from Fitness import User, UserNetwork
import JeevesLib

class TestFitness(unittest.TestCase):
  def setUp(self):
    # Need to initialize the JeevesLib environment.
    JeevesLib.init()

    self.alice = User(0)
    self.bob = User(1)
    self.carol = User(2)

    self.genericAverage = 3
    self.users = UserNetwork([self.alice, self.bob, self.carol])

  '''
  def testUserAverage(self):
    self.alice.addActivity(1)
    self.alice.addActivity(1)
    self.assertEqual(JeevesLib.concretize(self.users, self.alice.getAverageActivityLevel()))
  '''

if __name__ == '__main__':
    unittest.main()
