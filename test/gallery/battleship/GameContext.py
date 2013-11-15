import JeevesLib
from sourcetrans.macro_module import macros, jeeves

@jeeves
class GameContext:
  def __init__(self, user, game):
    self.user = user
    self.game = game
