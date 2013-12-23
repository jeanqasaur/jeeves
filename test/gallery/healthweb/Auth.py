import JeevesLib
from sourcetrans.macro_module import macros, jeeves

'''
TODO:
- Think about what Jeeves policies are good for here.
- Think about whether there is even any point of having credentials if we can
  just use Jeeves.
- Add @jeeves to things.
'''

class InternalAuthError(Exception):
  pass

class Cred:
  pass

class MkCred(Cred):
  def __init__(self, prin):
    self.prin = prin
  def __eq__(self, other):
    return self.prin == other.prin
  def __str__(self):
    return "Cred(" + self.prin.__str__() + ")"

class Prin:
  passwords = { 'Alice': 'AlicePW' }

  def login(self, pw):
    if isinstance(self, U):
      actualPwd = Prin.passwords[self.name]
      if actualPwd == pw:
        return MkCred(self)
      else:
        return None
    elif isinstance(self, Admin):
      if pw == "AdminPW":
        return MkCred(self)
      else:
        return None
    else:
      raise InternalAuthError

class U(Prin):
  def __init__(self, name):
    self.name = name
  def __eq__(self, other):
    return self.name == other.name
  def __str__(self):
    return self.name
class Admin(Prin):
  def __str__(self):
    return "Admin"
  def __eq__(self, other):
    return isinstance(other, Admin)
