import unittest
from datetime import *
import sys
sys.path.append("../../../..")
import JeevesLib
import macropy.activate
from smt.Z3 import *
sys.path.append("..")
from main import *
from users import *
from assignment import *
from submission import *

class TestCourseManager(unittest.TestCase):

  def setUp(self):
    JeevesLib.init()
    self.cm = CourseManager()
    user1 = Instructor(1,"jyang","Jean","Yang","jy@mit.edu")
    user1.setPassword("password")
    user2 = Student(2,"thance","Travis","Hance","th@mit.edu")
    user2.setPassword("password")
    user3 = Student(3,"bshaibu","Ben","Shaibu","bs@mit.edu")
    user3.setPassword("password")

    dueDate = datetime(2013, 11, 27, 12, 13, 14)
    dueDate = datetime(2013, 12, 10, 5, 5, 5)
    assignment1 = Assignment(1, "Documentation", dueDate, 100, "Create Documentation", 1)
    assignment2 = Assignment(2, "Create Application", dueDate, 100, "Create Application", 1)

    submission1 = Submission(1, "PyJeeves Docs", 1, 3, "This is Jeeves in Python!")
    submission2 = Submission(1, "CourseManager Docs", 1, 3, "This is a CourseManager in Python!")

    self.cm.userList = [user1, user2, user3]
    self.cm.assignmentList = [assignment1, assignment2]
    self.cm.submissionList = [submission1, submission2]

  def testInitialSystem(self):
    self.assertEqual(len(self.cm.userList), 3)
    self.assertEqual(len(self.cm.assignmentList), 2)
    self.assertEqual(len(self.cm.submissionList), 2)

  def testAccessUsers(self):
    user1 = Instructor(1,"jyang","Jean","Yang","jy@mit.edu")
    user1.setPassword("password")
    user2 = Student(2,"thance","Travis","Hance","th@mit.edu")
    user2.setPassword("password")
    user3 = Student(3,"bshaibu","Ben","Shaibu","bs@mit.edu")
    user3.setPassword("password")
    
    self.assertEqual(self.cm.userList[0], user1)
    self.assertEqual(self.cm.userList[1], user2)
    self.assertEqual(self.cm.userList[2], user3)

  def testAddUsers(self):
    user4 = Student(4,"sneaky","Sneaky","McSneak","sneak@mit.edu")
    user4.setPassword("password")
    user5 = Instructor(5,"asl", "Armando", "Solar-Lezama", "asl@mit.edu")
    user5.setPassword("password")

    self.assertTrue( self.cm.addStudent("sneaky","Sneaky","McSneak","sneak@mit.edu", "password") )
    self.assertTrue( self.cm.addInstructor("asl", "Armando", "Solar-Lezama", "asl@mit.edu", "password") )
    self.assertEqual( self.cm.userList[3], user4 )
    self.assertEqual( self.cm.userList[4], user5 )

  def testLogIn(self):
    user3 = Student(3,"bshaibu","Ben","Shaibu","bs@mit.edu")
    user3.setPassword("password")
    self.assertTrue(self.cm.log_in("bshaibu", "password"))
    self.assertEqual(self.cm.session, user3)

  def testViewStudentSubmission(self):
    self.cm.log_in("jyang", "password")
    print(self.cm.viewSubmissionDetails(1))

  def testViewYourSubmision(self):
    pass
  
  def testViewAnotherSubmission(self):
    pass

if __name__ == '__main__':
  unittest.main()
