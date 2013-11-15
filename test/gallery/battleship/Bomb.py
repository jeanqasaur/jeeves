import JeevesLib
from sourcetrans.macro_module import macros, jeeves

@jeeves
class Bomb:
  def __init__(self, owner):
    self.owner = owner
