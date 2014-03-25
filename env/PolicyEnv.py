import JeevesLib

import fast.AST
from collections import defaultdict
from eval.Eval import partialEval
from fast.AST import FExpr

from smt.Z3 import Z3

class SolverState:
    def __init__(self, policies_iterator, ctxt):
        self.solver = Z3()
        self.result = {}
        self.policies_iterator = policies_iterator
        self.ctxt = ctxt

    def concretizeExp(self, f, pathenv):
        f = fast.AST.fexpr_cast(f)

        while True:
            try:
                label, policy = self.policies_iterator.next()
            except StopIteration:
                break
            predicate = policy(self.ctxt) #predicate should be True if label can be HIGH
            predicate_vars = predicate.vars()
            constraint = partialEval(fast.AST.Implies(label, predicate), pathenv)

            if constraint.type != bool:
                raise ValueError("constraints must be bools")
            self.solver.boolExprAssert(constraint)
        
        if not self.solver.check():
            raise UnsatisfiableException("Constraints not satisfiable")

        vars_needed = f.vars()
        for var in vars_needed:
            if var not in self.result:
                self.solver.push()
                self.solver.boolExprAssert(var)
                if self.solver.isSatisfiable():
                    self.result[var] = True
                else:
                    self.solver.pop()
                    self.solver.boolExprAssert(fast.AST.Not(var))
                    self.result[var] = False
        
        assert self.solver.check()

        return f.eval(self.result)
        
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
  def restrict(self, label, policy, use_empty_env=False):
    pcFormula = fast.AST.Constant(True) if use_empty_env else JeevesLib.jeevesState.pathenv.getPathFormula()
    self.policies.append((label, lambda ctxt :
      fast.AST.Implies(
        pcFormula,
        fast.AST.fexpr_cast(policy(ctxt)),
      )
    ))

  def getNewSolverState(self, ctxt):
    return SolverState(self.policies.__iter__(), ctxt)

  def concretizeExp(self, ctxt, f, pathenv):
    solver_state = self.getNewSolverState(ctxt)
    return solver_state.concretizeExp(f, pathenv)

  """
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

    # NOTE(TJH): wtf? commenting this out to make stuff work
    # If a depends on b, then we want (b == Low ==> a == Low)
    #for (label, label_deps) in dependencies.iteritems():
    #  for label_dep in label_deps:
    #    constraints.append(fast.AST.Implies(label, label_dep))

    thevars = f.vars()
    env = smt.SMT.solve(constraints, self.labels[::-1], thevars)
    ev = f.eval(env)

    #print 'env is', {v.name:val for v, val in env.iteritems()}, 'ev is', ev
    return ev
  """
