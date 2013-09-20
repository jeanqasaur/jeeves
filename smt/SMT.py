'''
Translate expressions to SMT import format.
'''
from z3 import *

class SMT:
  # NOTE(JY): Think about if the solver needs to know about everything for
  # negative constraints. I don't think so because enough things should be
  # concrete that this doesn't matter.
  def solve(jeeveslib):
    # NOTE(JY): This is just a sketch of what should go on...
    # Implement defaults by adding values to the model and 
    for v in jeeveslib.env.envVars:
      jeeveslib.solver.push()
      solver.assertConstraint(v = z3.BoolVal(True))
      if (solver.check() == solver.Unsat):
        jeeveslib.solver.pop()

    # Now get the variables back from the solver by evaluating all
    # variables in question...

    # Now return the new environment...
    return NotImplemented
