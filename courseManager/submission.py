import macropy.activate
import sys
sys.path.append("..")
import JeevesLib
from user import *
from assignment import *
from smt.Z3 import *

class Submission():
  def __init__(self, submissionId, title, assignmentId, submitterId, fileRef):
    self.submissionId = submissionId
    self.title = title
    self.assignmentId = assignmentId
    self.sumitterId = submitterId
    self.fileRef = fileRef
    self.submittedOn = ""
    self.grade = None
    JeevesLib.init()
    
    ## Labels ##
    _viewerL = JeevesLib.mkLabel()
    _editorL = JeevesLib.mkLabel()
    _adminL = JeevesLib.mkLabel()
       
    ## Policies ##
    def _isUser(context):
      return isinstance(context, User)

    def _isSubmitter(context):
      return contextuserId == self.submitterId

    def _isInstructor(context):
      return isinstance(context, Instructor)

    JeevesLib.restrict(_viewerL, lambda oc: JeevesLib.jor(_isSubmitter(oc),  _isInstructor(oc)) )
    JeevesLib.restrict(_editorL, lambda oc: _isSubmitter(oc) )
    JeevesLib.restrict(_adminL, lambda oc: _isInstructor(oc) )

  ## Getter, Setters, and Show-ers ##   

  #Grade 
  def getGrade():
    score = JeevesLib.mkSensitive(_viewerL, self.grade, -1)
    return score

  def setGrade(score):
    # Would it be better to store score as a concretized value? 
    # It wouldn't work as well for a database, but possibly in simple examples
    self.grade = score

  def showGrade(context):
    return JeevesLib.concretize(context, self.getGrade())

  #Submission Details (fileRef)
  def getSubmissionDetails():
    details = JeevesLib.mkSensitive(_viewerL, self.fileRef, "N/A")
    return details

  def setSubmissionDetails(text):
    self.fileRef = text

  def showSubmissionDetails(context):
    return JeevesLib.concretize(context, self.getSubmissionDetails())
  
  #Submission Title
  def getTitle():
    details = JeevesLib.mkSensitive(_viewerL, self.title, "N/A")
    return details

  def setTitle(title):
    self.title = title

  def showTitle(context):
    return JeevesLib.concretize(context, self.getTitle())
  
  ## Magic Methods ##
  def __repr__(self):
    #Is there a way to integrate contexts with representation?
    #Would there be a point?    
    return "Submisison(%d, %s, %s)" % (self.submissionId, self.title, self.fileRef)

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.submissionId == other.submissionId and self.title == other.title
    else:
      return False

  def __ne__(self, other):
    return not self.__eq__(other)

if __name__ == '__main__':
  JeevesLib.init()
  print "Got Here"
  submission = Submission(1, "PyJeeves Docs", 1, 2, "This is Jeeves in Python!")
  submission2 = Submission(1, "CourseManager Docs", 1, 2, "This is a CourseManager in Python!")
  print(submission)
  print(submission2)
