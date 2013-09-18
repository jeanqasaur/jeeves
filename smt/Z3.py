'''
Defines the interface to the Z3 solver.
'''
# TODO: Define UnsatException and SolverException
import z3

class Z3Solver(Solver):
  def __init__(self):
    solver = Solver()
  # TODO: Is this the place to do this?
  #def __del__(self):
  #  z3.delete()

  # Defining variables.
  # TODO: Do we define them as functions in the Scala implementation?
  def declareInt(name):
    solver.Int(name)
  # TODO: Do things for declaring integers and that kind of thing...

  # TODO: Get this to return a Boolean?
  def check(): return solver.check()
  def eval(t):
    solver.eval(t)

  # TODO: Figure out if we pass a string or something else here. Probably a
  # string.
  def solverAssert(exprs):
    return solver.assert_exprs(exprs)

  def push(): solver.push()
  def pop(): solver.pop()
  def reset(): solver.reset_memory()
