import JeevesGlobal
import fast.AST

# TODO: Define your path variable environment, as well as manipulations, here.
class PathVars:
  def __init__(self):
    self.conditions = []

  def push(self, var, value):
    assert type(var) == fast.AST.Var
    assert type(value) == bool
    if (str(var), not value) in self.conditions:
      raise Exception("Path condition for '%s' already set to '%s'" % (var, not value))
    self.conditions.append((str(var), value))

  def pop(self):
    self.conditions.pop()

  def hasPosVar(self, var):
    return (str(var), True) in self.conditions

  def hasNegVar(self, var):
    return (str(var), False) in self.conditions

  def getPathFormula(self):
    if not self.conditions:
      return reduce(fast.AST.And, self.conditions, fast.AST.Constant(True))

class PositiveVariable:
  def __init__(self, var):
    self.var = var
  def __enter__(self):
    JeevesGlobal.jeevesLib.pathenv.push(self.var, True)
  def __exit__(self, type, value, traceback):
    JeevesGlobal.jeevesLib.pathenv.pop()

class NegativeVariable:
  def __init__(self, var):
    self.var = var
  def __enter__(self):
    JeevesGlobal.jeevesLib.pathenv.push(self.var, False)
  def __exit__(self, type, value, traceback):
    JeevesGlobal.jeevesLib.pathenv.pop()
