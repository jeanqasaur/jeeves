import JeevesLib
import fast.AST

class VarSetting:
  def __init__(self, var, val):
    self.var = var
    self.val = val
  def __eq__(self, other):
    return self.var is other.var and self.val == other.val
  def __str__(self):
    return "(%s, %s)" % (self.var.name, self.val)

# TODO: Define your path variable environment, as well as manipulations, here.
class PathVars:
  def __init__(self):
    self.conditions = []

  def push(self, var, value):
    assert type(var) == fast.AST.Var
    assert type(value) == bool
    if VarSetting(var, not value) in self.conditions:
      raise Exception("Path condition for '%s' already set to '%s'" % (var, not value))
    self.conditions.append(VarSetting(var, value))

  def pop(self):
    self.conditions.pop()

  def hasPosVar(self, var):
    return VarSetting(var, True) in self.conditions

  def hasNegVar(self, var):
    return VarSetting(var, False) in self.conditions

  def getPathFormula(self):
    c2 = [(vs.var if vs.val else fast.AST.Not(vs.var)) for vs in self.conditions]
    return reduce(fast.AST.And, c2, fast.AST.Constant(True))

  def getEnv(self):
    return {vs.var.name : vs.val for vs in self.conditions}
