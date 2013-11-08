import sys
sys.path.append("..")
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
    sum_x2 = sum([float(x**2) for x in l])
    stdev = math.sqrt((sum_x2 / len(l)) - (mean * mean)) 
    return stdev #check value

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

if __name__ == '__main__':
  due = datetime(2013, 11, 15, 12, 13, 14)
  a = Assignment(1, "Documentation", due, 100, "Create Documentation", 1)
  tlist = [1,2,4,5,6]
  print(a)
  print(a.average(tlist))
  print(a.std(tlist))
  print(a.median(tlist) )

























