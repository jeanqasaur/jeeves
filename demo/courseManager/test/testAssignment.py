import unittest
import math
from datetime import *
import sys
sys.path.append("../../../..")
import JeevesLib
sys.path.append("..")
from assignment import *

class TestAssignment(unittest.TestCase):

  def setUp(self):
    self.due = datetime(2013, 11, 15, 12, 13, 14)
    self.a = Assignment(1, "Documentation", self.due, 100, "Create Documentation", 1)
    self.tlist = [1,2,4,5,6]

  def testAverage(self):
    self.assertEqual(self.a.average(self.tlist), 3.6)

  def testMedian(self):
    self.assertEqual(self.a.median(self.tlist), 4)

  def testStandardDeviation(self):
    #2.0736
    self.assertEqual(round(self.a.std(self.tlist)), 2)

if __name__ == '__main__':
  unittest.main()
