'''
Translate expressions to SMT import format.
'''
class SMT:
  '''
  If we can find the variable in the environment, then we look it up and
  make that value into a string. Otherwise, we make the variable into a string.
  '''
  def variable(env):
    return NotImplemented

  '''
  Turns an expression f into a formula given an environment env and a scope sc.
  '''
  def formula(f, env, sc):
    # TODO: What is the Python equivalent of pattern-matching?
    return NotImplemented

  # TODO: Change everything so the defaults are high...?
  def solve(constraints, defaults, ):
    return NotImplemented
