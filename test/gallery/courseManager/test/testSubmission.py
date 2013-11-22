import unittest
import sys
sys.path.append("../../../..")
import JeevesLib
import macropy.activate
from smt.Z3 import *
sys.path.append("..")
from users import *
from assignment import *
from submission import *

class TestSubmission(unittest.TestCase):

  def setUp(self):
    JeevesLib.init()

  def testEquality(self):
    submission = Submission(1, "PyJeeves Docs", 1, 2, "This is Jeeves in Python!")
    submission1 = Submission(1, "PyJeeves Docs", 1, 2, "This is Jeeves in Python!")
    submission2 = Submission(1, "CourseManager Docs", 1, 2, "This is a CourseManager in Python!")
    self.assertEqual(submission,submission1)
    self.assertNotEqual(submission,submission2)

if __name__ == '__main__':
  unittest.main()
