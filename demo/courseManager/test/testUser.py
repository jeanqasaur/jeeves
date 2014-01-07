import unittest
import hashlib
import sys
sys.path.append("..")
from users import *
sys.path.append("../../../..")
import JeevesLib

class TestUser(unittest.TestCase):

  def setUp(self):
    pass

  def testPasswordValidation(self):
    self.user = User(1,"bob","Bob","Barker","bbarker@mit.edu")
    self.user.setPassword("password")
    self.assertTrue( self.user.validate("password") )

  def testEquality(self):
    a = User(1,"bob","Bob","Barker","bbarker@mit.edu")
    b = User(1,"bob","Bob","Barker","bbarker@mit.edu")
    c = User(2,"stew","Stu","Pickle","spickle@mit.edu")
    self.assertEqual(a,b)
    self.assertNotEqual(a,c)
    bobTeacher = Instructor(1,"bob","Bob","Barker","bbarker@mit.edu")
    bobStudent = Student(1,"bob","Bob","Barker","bbarker@mit.edu")
    self.assertNotEqual(bobTeacher, bobStudent)

if __name__ == '__main__':
  unittest.main()
