'''
Fitness example for Jeeves with confidentiality policies.
'''
import datetime
import operator

import JeevesLib
from sourcetrans.macro_module import macros, jeeves

class InternalError(Exception):
  def __init__(self, message):
    self.message = message

# Definitions of locations.
@jeeves
class User:
  def __init__(self, userId):
    self.userId = userId
    self.activity = {}

  def addActivity(self, activity):
    # Confidentiality policy: 
    self.activity[datetime.date] = activity

  # POLICY: If there are more than k people who have similar profile like Jean,
  # then uses avgActivityLevelJean as the real value to compute the group
  # average; else use the existing group average avgActivityLevelinstead. This
  # means that adding Jean's value avgActivityLevelJean will not change the
  # group's average and will not be picked out as outliner. 
  def getAverageActivityLevel(self):
    a = JeevesLib.mkLabel('activity_label')
 
    # Compute average activity level.
    activityValues = self.activity.values()
    # TODO: We really want this to be the average activity level of the
    # *output channel* and not the current activity level...
    genericAverage = 3
    averageActivity = reduce(operator.add, activityValues, 0) / len(activityValues) if len(activityValues) > 0 else genericAverage
    # Can see the average activity level if there are at least 3 with averages
    # within 0.2.
    JeevesLib.restrict(a
      , lambda oc: oc.atLeastKSimilar(averageActivity, 2, 0.2))
    activityLevel = JeevesLib.mkSensitive(a, averageActivity, genericAverage)
    return activityLevel

# TODO: Is this just the view context?
@jeeves
class UserNetwork:
  def __init__(self, users=[]):
    self.users = users

  def getAverageActivityLevel(self):
    userSum = reduce(lambda acc, u: acc + u.averageActivityLevel(), self.users)
    return userSum / len(self.users)

  def atLeastKSimilar(self, avg, k, delta):
    count = 0
    for user in self.users:
      userAvg = user.getAverageActivityLevel()
      if (avg - delta) < userAvg and userAvg < (avg + delta):
        count += 1
    return count >= k
