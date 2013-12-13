import sys
sys.path.append("../../..")
import JeevesLib
import macropy.activate
from smt.Z3 import *

from users import *
from assignment import *
from submission import *
from datetime import *

#TODO Make all variables "private" -> add _variableName
class CourseManager:
  def __init__(self):
    JeevesLib.init()
    self.assignmentList = []
    self.userList = []
    self.submissionList = []
    self.session = None

  def log_in(self, username, password):
    user = self.userList[self.userNameToIndex(username)]
    if user.validate(password):
      self.session = user
      return True
    else:
      return False

  def log_out(self):
    self.session = none
    return True

  def addStudent(self, uName, fName, lName, email, password):
    sId = len(self.userList)+1
    stud = Student(sId, uName, fName, lName, email)
    stud.setPassword(password)
    self.userList.append(stud)
    if len(self.userList) == sId:
      return True
    else:
      return False

  def addInstructor(self, uName, fName, lName, email, password):
    insId = len(self.userList)+1
    ins = Instructor(insId, uName, fName, lName, email)
    ins.setPassword(password)
    self.userList.append(ins)
    if len(self.userList) == insId:
      return True
    else:
      return False

  def userNameToIndex(self,name):
    for x in xrange(len(self.userList)):
      user = self.userList[x]
      if user.userName == name:
        return x
      else:
        -1

  def addAssignment(self, aName, due, maxPoints, prompt):
    if isinstance(session, Instructor):
      aId = len(self.assignmentList) + 1
      assg = Assignment(aId, aName, due, maxPoints, prompt, session.userId)
      self.assignmentList.append(assg)
    return isinstance(session, Instructor)

  def viewAssignment(self, name):
    for x in xrange(len(self.assignmentList)):
      assignment = self.assignmentList[x]
      if assignment.name == name:
        return assignment
    return None

  def addSubmission(self, assignmentId, title, text):
    if isinstance(self.session, Student):
      sId = len(self.submissionList) + 1
      submission = Submission(sId, title, assignmentId, self.session.userId, text)
      self.submissionList.append(submission)
    return isinstance(self.session, Student)

  def viewSubmissionDetails(self, sId):
    submission = self.submissionList[sId-1]
    title = submission.showTitle(self.session)
    details = submission.showSubmissionDetails(self.session)
    grade = submission.showGrade(self.session)
    return "Submission(%s, %s, %d)" % (title, details, grade)

  #Incomplete
  def viewSubmissionFromUser(self, assignment, userName):
    for x in xrange(len(submissionList)):
      assignment = self.assignmentList[x]
      if assignment.name == name:
        return assignment

if __name__ == '__main__':
  cm = CourseManager()
  cm.addInstructor("jyang", "Jean", "Yang", "jy@mit.edu", "password")
  cm.addStudent("thance","Travis","Hance","th@mit.edu","password")
  cm.addStudent("bshaibu","Ben","Shaibu","bs@mit.edu", "password")
  while cm.session is None:
    print("Log In")
    uname = raw_input("Username: ")
    pword = raw_input("Password: ")
    if cm.log_in(uname, pword):
      print("Log In Successful!")
      print(cm.session)
    else:
      print ("Log In Failed.") 

