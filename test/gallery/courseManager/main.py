from user import *
from assignment import *
from datetime import *

#Pre-Users
a = Instructor(1,"jyang","Jean","Yang","jy@mit.edu")
a.setPassword("password")
b = Student(2,"thance","Travis","Hance","th@mit.edu")
b.setPassword("password")
c = Student(3,"bshaibu","Ben","Shaibu","bs@mit.edu")
c.setPassword("password")
due = datetime(2013, 11, 15, 12, 13, 14)
assg = Assignment(1, "Documentation", due, 100, "Create Documentation", 1)

assignmentList = [assg]
userList = [a, b, c]
submissionList = []
session = None

def userNameToIndex(name):
  for x in xrange(len(userList)):
    user = userList[x]
    if user.userName == name:
      return x
    else:
      -1

def addAssignment(aName, due, maxPoints, prompt):
  if isinstance(session, Instructor):
    aId = len(assignmentList)
    assg = Assignment(aId, aName, due, maxPoints, prompt, session.userId)
    assignmentList.append(assg)
  return isinstance(session, Instructor)

def viewAssignment(name):
  for x in xrange(len(assignmentList)):
    assignment = assignmentList[x]
    if assignment.name == name:
      return assignment
  return None

def addSubmission(assignmentId, title, text):
  if isinstance(session, Instructor):
    sId = len(submissionList)
    submission = Submission(sId, title, assignmentId, session.userId, text)
    submissionList.append(submission)
  return isinstance(session, Instructor)

def viewSubmissionDetails(sId):
  submission = submissionList[sid]
  title = showTitle(session)
  details = showSubmissionDetails(session)
  grade = showGrade(session)
  return "Submission(%s, %s, %d)" % (title, details, grade)

def viewSubmissionFromUser(assignment, userName):
  for x in xrange(len(submissionList)):
    assignment = assignmentList[x]
    if assignment.name == name:
      return assignment

if __name__ == '__main__':
  JeevesLib.init()
  while session is None:
    print("Log In")
    uname = raw_input("Username: ")
    pword = raw_input("Password: ")
    user = userList[userNameToIndex(uname)]
    if user.validate(pword):
      session = user
      print("Log In Successful!")
    else:
      print ("Log In Failed.")
  

