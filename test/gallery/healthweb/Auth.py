import JeevesLib
from macropy.case_classes import macros, case
from macropy.experimental.pattern import macros, switch
from sourcetrans.macro_module import macros, jeeves

@jeeves
class Authentication:

  @case
  class Prin():
    pass
    '''
    class U(name):
      def __eq__(self, other):
        self.name == other.name
    class Admin:
      pass
    '''

  @case
  class Cred():
    pass
    '''
    class MkCred(prin):
      def __eq__(self, other):
        self.prin == other.prin
    '''

  def login(self, p, pw):
    pass
    '''
    with switch(p, pw):
      if (U("Alice"), "AlicePW"):
        return Cred.MkCred(p)
      elif (Admin, "AdminPW"):
        return Cred.MkCred(p)
      else:
        return None
    '''
