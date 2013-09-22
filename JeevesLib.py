'''
This will define the code for the Jeeves library.
'''
from env.VarEnv import VarEnv
from env.PathVars import PathVars
from smt.Z3 import Z3

# NOTE(JY): I was thinking we can keep around a copy of JeevesLib globally or
# something like that and it will store all of our environments...
class JeevesLib:
  def __init__(self):
    self.solver = Z3()
    self.varenv = VarEnv()
    self.pathenv = PathVars()
    self.labelCount = 0

  # NOTE(JY): We have to take care of the scoping somehow to make sure that
  # we don't duplicate variables. One potential solution we can do, though, is
  # to have a tight coupling with the solver where
  def mkLabel(self, varName = ""):
    if not varName:
      # TODO: Make sure the double underscore works in the solver...
      varName = '__x' + str(self.labelCount)
      self.labelCount += 1
    # TODO: Add this label to the environment.
    return self.solver.getBoolVar(varName)

  # NOTE(JY): Maybe we can just define a macro transformation here and interact
  # directly with the environment.
  # I think we can do this quite nicely by defining a mapping from our AST
  # expressions to Z3 expressions and then directly adding those to the solver.
  def restrict(self, varLabel, pred):
    # 1. Walk over the predicate AST and turn it into a Z3 formula.
    # 2. Add the formula (not pred) ==> (varLabel == false) to the constraint
    #    environment.

    # NOTE(JY): This should never be unsat...
    return NotImplemented

  def mkSensitive(self, varLabel, vHigh, vLow):
    return NotImplemented

  # TODO: Push a context, try setting things to high 
  def concretize(self, ctxt, v):
    return NotImplemented
