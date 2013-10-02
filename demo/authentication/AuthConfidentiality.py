'''
Authentication demo example for Jeeves with confidentiality policies.
'''
import JeevesGlobal

class Principal:
  class User:
    def __init__(self, userId, name, pwd):
      self.userId = userId
      self.name = name
      self.pwdLabel = JeevesGlobal.jeevesLib.mkLabel()
      JeevesGlobal.jeevesLib.restrict(self.pwdLabel, lambda oc: oc == self)
      # If we do it this other way, we can do a cute thing where we construct a
      # user from information they enter and use that to authenticate the login.
      #JeevesGlobal.jeevesLib.restrict(self.pwdLabel
      #    , lambda oc: Util.jand(oc.userId == self.userId
      #         , Util.jand(oc.name == self.name, oc.getPwd() == self.getPwd())))
      self.pwd = JeevesGlobal.jeevesLib.mkSensitive(self.pwdLabel, pwd, "")

    def getPwd(self): return self.pwd
  class NullUser:
    pass

class Authentication:
  @staticmethod
  def login(prin, pwd):
    if isinstance(prin, Principal.User):
      JeevesGlobal.jeevesLib.jif (prin.getPwd() == pwd
          , (lambda: prin)
          , (lambda: Principal.NullUser()))
