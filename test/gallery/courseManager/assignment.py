import sys
sys.path.append("../../..")
import JeevesLib
import math
from datetime import *

class Assignment():
  def __init__(self, assignmentId, name, dueDate, maxPoints, prompt, authorId):
    self.assignmentId = assignmentId
    self.name = name
    self.dueDate = dueDate
    self.maxPoints = maxPoints
    self.prompt = prompt
    self.authorId = authorId
    
  # Labels
  # Policies

  def __repr__(self):
    return "Assignment(%d, %s, %s)" % (self.assignmentId, self.name, self.prompt)

  # Math Functions
  def average(self, l):
    return float(sum(l))/len(l)

  def std(self, l):
    mean = self.average(l)
    variance = map(lambda x: (float(x) - mean)**2, l)
    stdev = math.sqrt(self.average(variance))
    return stdev #check precision

  def median(self, l):
    sortedL = sorted(l)
    length = len(sortedL)
    if length % 2:          
      return sortedL[length / 2]
    else:
      return self.average( sortedL[length / 2], sortedL[length/2 - 1] )
     
  # Get

  # Set

  # Show






















