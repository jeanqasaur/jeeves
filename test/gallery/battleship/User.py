import JeevesLib
from sourcetrans.macro_module import macros, jeeves

@jeeves
class User:
  def __init__(self, userId, name=""):
    self.userId = userId
    self.name = name
  def __eq__(self, other):
    return self.userId == other.userId
  def __hash__(self):
    return self.userId
