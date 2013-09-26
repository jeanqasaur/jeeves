'''
Translate expressions to SMT import format.
'''
from Z3 import Z3

class UnsatisfiableException(Exception):
    pass

# NOTE(JY): Think about if the solver needs to know about everything for
# negative constraints. I don't think so because enough things should be
# concrete that this doesn't matter.
def solve(constraints, defaults, env):
  # NOTE(JY): This is just a sketch of what should go on...
  # Implement defaults by adding values to the model and 

  #for v in jeeveslib.env.envVars:
  #  jeeveslib.solver.push()
  #  solver.assertConstraint(v = z3.BoolVal(True))
  #  if (solver.check() == solver.Unsat):
  #    jeeveslib.solver.pop()

  # Now get the variables back from the solver by evaluating all
  # variables in question...

  # Now return the new environment...
  #return NotImplemented

  solver = Z3()

  for constraint in constraints:
    if constraint.type != bool:
      raise ValueError("constraints must be bools")
    solver.addAssertion(constraint)

  if not solver.check():
    raise UnsatisfiableException("Constraints not satisfiable")

  for default in defaults:
    solver.push()
    if default.type != bool:
      raise ValueError("defaults must be bools")
    solver.addAssertion(default)
    if not solver.check():
      solver.pop()

  assert solver.check()

  allVars = set()
  for constraint in constraints:
    allVars |= constraint.vars()

  env = dict(env)
  for var in allVars:
    if var not in env:
      env[var] = solver.getVar(var)

  return env
