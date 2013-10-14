import JeevesLib
import fast.AST

# TODO: Define your path variable environment, as well as manipulations, here.
class PathVars:
  def __init__(self):
    self.conditions = []

  def push(self, var, value):
    assert type(var) == fast.AST.Var
    assert type(value) == bool
    if (var, not value) in self.conditions:
      raise Exception("Path condition for '%s' already set to '%s'" % (var, not value))
    self.conditions.append((var, value))

  def pop(self):
    self.conditions.pop()

  def hasPosVar(self, var):
    return (var, True) in self.conditions

  def hasNegVar(self, var):
    return (var, False) in self.conditions

  def getPathFormula(self):
    c2 = [(var if val else fast.AST.Not(var)) for (var, val) in self.conditions]
    return reduce(fast.AST.And, c2, fast.AST.Constant(True))

  def getEnv(self):
    return dict(self.conditions)
