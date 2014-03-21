import JeevesLib

import fast.AST
import smt.SMT
from collections import defaultdict
from eval.Eval import partialEval
from fast.AST import FExpr

class PolicyEnv:
  def __init__(self):
    self.labels = []
    self.policies = []

  def mkLabel(self, name="", uniquify=True):
    label = fast.AST.Var(name, uniquify)
    self.labels.append(label)
    return label

  # policy is a function from context to bool which returns true
  # if the label is allowed to be HIGH
  def restrict(self, label, policy):
    pcFormula = JeevesLib.jeevesState.pathenv.getPathFormula()
    self.policies.append((label, lambda ctxt :
      fast.AST.Implies(
        pcFormula,
        fast.AST.fexpr_cast(policy(ctxt)),
      )
    ))

  # Takes a context and an expression
  def concretizeExp(self, ctxt, f, pathenv):
    f = fast.AST.fexpr_cast(f)
    dependencies = defaultdict(set)
    constraints = []
    # First, find all all the dependencies between labels
    # and add Not(predicate) ==> label == LOW conditions
    for label, policy in self.policies:
      predicate = policy(ctxt) #predicate should be True if label can be HIGH
      predicate_vars = predicate.vars()
      dependencies[label] |= predicate_vars
      constraints.append(partialEval(fast.AST.Implies(label, predicate), pathenv))

    # If a depends on b, then we want (b == Low ==> a == Low)
    for (label, label_deps) in dependencies.iteritems():
      for label_dep in label_deps:
        constraints.append(fast.AST.Implies(label, label_dep))

    thevars = f.vars()
    env = smt.SMT.solve(constraints, self.labels[::-1], thevars)
    ev = f.eval(env)

    return ev
