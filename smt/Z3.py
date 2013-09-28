'''
Defines the interface to the Z3 solver.
'''
# TODO: Define UnsatException and SolverException
import z3

class Z3:
  def __init__(self):
    self.solver = z3.Solver()

  # TODO: Is this the place to do this?
  #def __del__(self):
  #  z3.delete()

  # Defining variables.
  def getIntVar(self, name):
    return z3.Int(name)

  def getBoolVar(self, name):
    return z3.Bool(name)

  def check(self):
    return self.solver.check()

  def isSatisfiable(self):
    r = self.solver.check()
    if r == z3.sat:
      return True
    elif r == z3.unsat:
      return False
    else:
      raise ValueError("got neither sat nor unsat from solver")

  def evaluate(self, t):
    s = self.solver.model().eval(t.z3Node())
    assert z3.is_true(s) or z3.is_false(s)
    return z3.is_true(s)

  def solverAssert(self, constraint):
    return self.solver.add(constraint)

  def boolExprAssert(self, constraint):
    return self.solver.add(constraint.z3Node())

  def push(self):
    self.solver.push()

  def pop(self):
    self.solver.pop()

  def reset(self):
    self.solver.reset_memory()
