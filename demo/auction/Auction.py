'''
Authentication demo example for Jeeves with confidentiality policies.
'''

import JeevesGlobal
from fast.AST import And

class User:
  def __init__(self, userId, name, pwd):
    self.userId = userId
    self.name = name
    self.pwdLabel = JeevesGlobal.jeevesLib.mkLabel()
    # TODO`: Figure out how deep this equality goes...
    #JeevesGlobal.jeevesLib.restrict(self.pwdLabel
    #    , lambda oc: And(oc.userId == self.userId
    #         , And(oc.name == self.name, oc.getPwd() == self.getPwd())))
    self.pwd = JeevesGlobal.jeevesLib.mkSensitive(self.pwdLabel, pwd, "")

  def getPwd(self): return self.pwd
