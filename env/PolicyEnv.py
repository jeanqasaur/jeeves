"""Policy environment.
    
    :synopsis: Functionality corresponding to storing labels and policies and
    interacting with the solver.

    .. moduleauthor:: Travis Hance <tjhance7@gmail.com>
    .. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
import JeevesLib

import fast.AST
from collections import defaultdict
from fast.AST import Constant, FExpr

from smt.Z3 import Z3
from weakref import WeakKeyDictionary

class SolverState:
    def __init__(self, policies, ctxt):
        self.solver = Z3()
        self.result = {}
        self.ctxt = ctxt

        self.policies = policies
        # self.policies_index = 0

    def getLabelClosure(self, varsNeeded):
        for label in varsNeeded:
            if self.policies.has_key(label):
                policy = self.policies[label]

                varsNeeded = varsNeeded.union(policy(self.ctxt).vars())
        return varsNeeded

    def solvePolicies(self, varsNeeded, pathenv):
        assignedVars = True
        constraints = []

        # Get relevant policies.
        for label in varsNeeded:
            assignedVar = False
            # If there are policies associated with the label.
            if self.policies.has_key(label):
                policy = self.policies[label]

                #predicate should be True if label can be HIGH
                predicate = policy(self.ctxt).partialEval(pathenv)
                constraint = fast.AST.Implies(
                                label, predicate).partialEval(pathenv)

                # If the predicate is a constant, this means there are no
                # dependencies on other labels so we can simply evaluate the
                # policy.
                if predicate.type != bool:
                    raise ValueError("constraints must be bools")
                if isinstance(predicate, Constant):
                    if not predicate.v:
                        self.result[label] = False
                    else:
                        self.result[label] = True
                    assignedVar = True
                constraints.append(constraint)
            else:
                pass
            assignedVars = assignedVars and assignedVar

        if not assignedVars:
            for constraint in constraints:
                self.solver.boolExprAssert(constraint)

            for var in varsNeeded:
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

    def concretizeExp(self, f, pathenv):
        """
        Expression concretization.
        """
        f = fast.AST.fexpr_cast(f)

        # Get transitive closure of variables mentioned in both the labels and
        # the policies.
        # TODO: Make this more efficient.
        vars_needed = f.vars()
        for label in vars_needed:
            if self.policies.has_key(label):
                policy = self.policies[label]
                vars_needed = vars_needed.union(policy(self.ctxt).vars())

        # Get relevant policies.
        for label in vars_needed:
            # If there are policies associated with the label.
            if self.policies.has_key(label):
                policy = self.policies[label]

                #predicate should be True if label can be HIGH
                predicate = policy(self.ctxt)
            
                predicate_vars = predicate.vars()
                constraint = fast.AST.Implies(
                                label, predicate).partialEval(pathenv)

                if constraint.type != bool:
                    raise ValueError("constraints must be bools")
                self.solver.boolExprAssert(constraint)

        # Make sure environment is satisfiable.
        if not self.solver.check():
            raise UnsatisfiableException("Constraints not satisfiable")
 
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

        JeevesLib.log_counts(len(vars_needed))

        return f.eval(self.result)

    def assignLabel(self, label, pathenv):
        if label in self.result:
            return self.result[label]
        else:
            varsNeeded = self.getLabelClosure({label})
            self.solvePolicies(varsNeeded, pathenv)

            JeevesLib.log_counts(len(varsNeeded))

            return self.result[label]

class PolicyEnv:
  def __init__(self):
    self.policies = WeakKeyDictionary()

  def mkLabel(self, name="", uniquify=True):
    label = fast.AST.Var(name, uniquify)
    return label

  # policy is a function from context to bool which returns true
  # if the label is allowed to be HIGH
  def restrict(self, label, policy, use_empty_env=False):
    pcFormula = fast.AST.Constant(True) if use_empty_env \
                    else JeevesLib.jeevesState.pathenv.getPathFormula()
    
    label_var_set = label.vars()
    assert(len(label_var_set) == 1)
    label_var = list(label_var_set)[0]
    if self.policies.has_key(label_var):
        self.policies[label_var] = (lambda ctxt:
            fast.AST.Implies(
                pcFormula,
                fast.AST.And(fast.AST.fexpr_cast(policy(ctxt))
                    , fast.AST.fexpr_cast(self.policies[label_var](ctxt)))))
    else:
        self.policies[label_var] = (lambda ctxt:
            fast.AST.Implies(
                pcFormula,
                fast.AST.fexpr_cast(policy(ctxt)),
            ))

  def getNewSolverState(self, ctxt):
    return SolverState(self.policies, ctxt)

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
