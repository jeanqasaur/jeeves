import JeevesLib

import fast.AST
import smt.SMT
from collections import defaultdict

class PolicyEnv:
  def __init__(self):
    self.labels = []
    self.policies = {}

  def mkLabel(self, name=""):
    label = fast.AST.Var(name)
    self.labels.append(label)
    return label

  # policy is a function from context to bool which returns true
  # if the label is allowed to be HIGH
  def restrict(self, label, policy):
    pcFormula = JeevesLib.jeevesState.pathenv.getPathFormula()
    self.policies[label] = (lambda ctxt :
      fast.AST.Implies(
        pcFormula,
        fast.AST.fexpr_cast(policy(ctxt)),
      )
    )

  # Takes a context and an expression
  def concretizeExp(self, ctxt, f):
    f = fast.AST.fexpr_cast(f)
    dependencies = defaultdict(set)
    constraints = []
    # First, find all all the dependencies between labels
    # and add Not(predicate) ==> label == LOW conditions
    for (label, policy) in self.policies.iteritems():
      predicate = policy(ctxt) #predicate should be True if label can be HIGH
      predicate_vars = predicate.vars()
      dependencies[label] |= predicate_vars
      constraints.append(fast.AST.Implies(label, predicate))

    # If a depends on b, then we want (b == Low ==> a == Low)
    for (label, label_deps) in dependencies.iteritems():
      for label_dep in label_deps:
        constraints.append(fast.AST.Implies(label, label_dep))

    env = smt.SMT.solve(constraints, self.labels[::-1], f.vars())

    return f.eval(env)
