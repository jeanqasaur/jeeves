'''
Authentication demo example for Jeeves with confidentiality policies.
'''
import JeevesLib
from sourcetrans.macro_module import macros, jeeves

@jeeves
class Principal:
  class User:
    def __init__(self, userId, name, pwd):
      self.userId = userId
      self.name = name

      # Sensitive password.
      self.pwdLabel = JeevesLib.mkLabel()
      JeevesLib.restrict(self.pwdLabel, lambda oc:
        oc.pwd == self.pwd if isinstance(oc, Principal.User) else False)
      self.pwd = JeevesLib.mkSensitive(self.pwdLabel, pwd, "")

    def __eq__(self, other):
      return self.userId == other.userId
  class NullUser:
    def __eq__(self, other):
      return isinstance(other, Principal.NullUser)

class Authentication:
  @staticmethod
  @jeeves
  def login(prin, pwd):
    if isinstance(prin, Principal.User):
      return prin if (prin.pwd == pwd) else Principal.NullUser()
