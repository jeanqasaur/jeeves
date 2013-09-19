'''
Defines the interface to the Z3 solver.
'''
# TODO: Define UnsatException and SolverException
import z3
from Solver import *

class Z3(Solver):
  def __init__(self):
    self.solver = z3.Solver()
  # TODO: Is this the place to do this?
  #def __del__(self):
  #  z3.delete()

  # Defining variables.
  def declareInt(self, name): return z3.Int(name)

  def check(self):
    r = self.solver.check()
    if r == z3.sat:
      return self.Sat
    elif r == z3.unsat:
      return self.Unsat
    else:
      return self.Unknown
  def eval(self, t): self.solver.eval(t)

  # TODO: Figure out if we pass a string or something else here. Probably a
  # string.
  def solverAssert(self, constraint):
    return self.solver.add(constraint)

  def push(self): self.solver.push()
  def pop(self): self.solver.pop()
  def reset(self): self.solver.reset_memory()
