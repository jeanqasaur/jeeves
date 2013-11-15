import JeevesLib
from sourcetrans.macro_module import macros, jeeves

@jeeves
class User:
  def __init__(self, userId):
    self.userId = userId
  def __eq__(self, other):
    return self.userId == other.userId
  def __hash__(self):
    return self.userId
