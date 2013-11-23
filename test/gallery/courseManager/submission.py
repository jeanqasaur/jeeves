from datetime import *

import sys
sys.path.append("../../..")
import JeevesLib
from smt.Z3 import *
import macropy.activate

from users import *
from assignment import *

class Submission():
  def __init__(self, submissionId, title, assignmentId, submitterId, fileRef):
    self.submissionId = submissionId
    self.title = title
    self.assignmentId = assignmentId
    self.submitterId = submitterId
    self.fileRef = fileRef
    self.submittedOn = ""
    self.grade = None
    self.submittedOn = datetime.now()
    JeevesLib.init()

    ## Policies ##
    def _isUser(context):
      return isinstance(context, User)

    def _isSubmitter(context):
      return context.userId == self.submitterId

    def _isInstructor(context):
      return isinstance(context, Instructor)
    
    ## Labels ##
    self._viewerL = JeevesLib.mkLabel()
    self._editorL = JeevesLib.mkLabel()
    self._adminL = JeevesLib.mkLabel()
  
    ## Restrict Labels ##
    JeevesLib.restrict(self._viewerL, lambda oc: JeevesLib.jor(_isSubmitter(oc),  _isInstructor(oc) ) )
    JeevesLib.restrict(self._editorL, lambda oc: _isSubmitter(oc) )
    JeevesLib.restrict(self._adminL, lambda oc: _isInstructor(oc) )

  ## Getter, Setters, and Show-ers ##   

  #Grade 
  def getGrade(self):
    score = JeevesLib.mkSensitive(_viewerL, self.grade, -1)
    return score

  def setGrade(self,score):
    # Would it be better to store score as a concretized value? 
    # It wouldn't work as well for a database, but possibly in simple examples
    self.grade = score

  def showGrade(self, context):
    return JeevesLib.concretize(context, self.getGrade())

  #Submission Details (fileRef)
  def getSubmissionDetails(self):
    details = JeevesLib.mkSensitive(self._viewerL, self.fileRef, "N/A")
    return details

  def setSubmissionDetails(self, text):
    self.fileRef = text

  def showSubmissionDetails(self, context):
    return JeevesLib.concretize(context, self.getSubmissionDetails())
  
  #Submission Title
  def getTitle(self):
    details = JeevesLib.mkSensitive(self._viewerL, self.title, "N/A")
    return details

  def setTitle(self, title):
    self.title = title

  def showTitle(self, context):
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
