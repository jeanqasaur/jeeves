import sys
sys.path.append("../../..")
import JeevesLib
import hashlib

class User:
  def __init__(self, userId, userName, firstName, lastName, email):
    self.userId = userId
    self.userName = userName
    self.firstName = firstName
    self.lastName = lastName
    self.email = email
    self._passwordDigest = ""

  def __repr__(self):
    return "User(%d, %s)" % (self.userId, self.userName)

  # Labels

  # Policies

  ## Password Functions ##
  def md5(self, string):
    return hashlib.md5(string).hexdigest()

  def setPassword(self, password):
    self._passwordDigest = self.md5(password)

  def validate(self, password):
    return self._passwordDigest == self.md5(password)

  ## Actions ##
  def submitAssignment(self, assignment, name):
    pass
  
  def createAssignment(self, assignmentname, dueDate, maxPoints, prompt):
    pass
  
  ## Magic Methods ##
  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.userId == other.userId and self.userName == other.userName
    else:
      return False

  def __ne__(self, other):
    return not self.__eq__(other)
    
class Student(User):
  def __init__(self, userId, userName, firstName, lastName, email):
    User.__init__(self, userId, userName, firstName, lastName, email)

class Instructor(User):
  def __init__(self, userId, userName, firstName, lastName, email):
    User.__init__(self, userId, userName, firstName, lastName, email)
