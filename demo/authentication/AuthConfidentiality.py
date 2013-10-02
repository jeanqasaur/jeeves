'''
Authentication demo example for Jeeves with confidentiality policies.
'''
import JeevesGlobal
#import fast.AST

class User:
  def __init__(self, userId, name, pwd):
    self.userId = userId
    self.name = name
    self.pwdLabel = JeevesGlobal.jeevesLib.mkLabel()
    # TODO: Can we check equality like this? If we do it right, there should
    # be a circular dependency on the password equality. (Is that right?)
    JeevesGlobal.jeevesLib.restrict(self.pwdLabel, lambda oc: oc == self)
    self.pwd = JeevesGlobal.jeevesLib.mkSensitive(self.pwdLabel, pwd, "")

  def getPwd(self): return self.pwd
