'''
This will define the code for the Jeeves library.
'''
from env.VarEnv import VarEnv
from env.PolicyEnv import PolicyEnv
from env.PathVars import PathVars, PositiveVariable, NegativeVariable
from smt.Z3 import Z3
from fast.AST import Facet, fexpr_cast, Constant, Var, Not, FExpr
from eval.Eval import partialEval
import JeevesGlobal

# NOTE(JY): I was thinking we can keep around a copy of JeevesLib globally or
# something like that and it will store all of our environments...
class JeevesLib:
  def __init__(self):
    self.solver = Z3()
    self.varenv = VarEnv()
    self.pathenv = PathVars()
    self.policyenv = PolicyEnv()

  # NOTE(JY): We have to take care of the scoping somehow to make sure that
  # we don't duplicate variables. One potential solution we can do, though, is
  # to have a tight coupling with the solver where
  def mkLabel(self, varName = ""):
    return self.policyenv.mkLabel(varName)

  # NOTE(JY): Maybe we can just define a macro transformation here and interact
  # directly with the environment.
  # I think we can do this quite nicely by defining a mapping from our AST
  # expressions to Z3 expressions and then directly adding those to the solver.
  def restrict(self, varLabel, pred):
    # 1. Walk over the predicate AST and turn it into a Z3 formula.
    # 2. Add the formula (not pred) ==> (varLabel == false) to the constraint
    #    environment.

    # NOTE(JY): This should never be unsat...
    self.policyenv.restrict(varLabel, pred)

  def mkSensitive(self, varLabel, vHigh, vLow):
    return Facet(varLabel, fexpr_cast(vHigh), fexpr_cast(vLow))

  # TODO: Push a context, try setting things to high 
  def concretize(self, ctxt, v):
    return self.policyenv.concretizeExp(ctxt, v)

  def jif(self, cond, thn_fn, els_fn):
    condTrans = partialEval(fexpr_cast(cond))
    if condTrans.type != bool:
      raise TypeError("jif must take a boolean as a condition")
    return self.jif2(condTrans, thn_fn, els_fn)

  def jif2(self, cond, thn_fn, els_fn):
    if isinstance(cond, Constant):
      return thn_fn() if cond.v else els_fn()

    #elif isinstance(cond, Var):
    #  with PositiveVariable(cond):
    #    thn = thn_fn()
    #  with NegativeVariable(cond):
    #    els = els_fn()
    #  return Facet(cond, fexpr_cast(thn), fexpr_cast(els))

    elif isinstance(cond, Facet):
      if not isinstance(cond.cond, Var):
        raise TypeError("facet conditional is of type %s"
                        % cond.cond.__class__.__name__)
      hasP = self.pathenv.hasPosVar(cond.cond)
      hasN = self.pathenv.hasNegVar(cond.cond)

      if not hasN:
        with PositiveVariable(cond.cond):
          thn = self.jif2(cond.thn, thn_fn, els_fn)
      if not hasP:
        with NegativeVariable(cond.cond):
          els = self.jif2(cond.els, thn_fn, els_fn)

      if hasP:
        return thn
      elif hasN:
        return els
      else:
        return Facet(cond.cond, thn, els)

    else:
      raise TypeError("jif condition must be a constant or a var")

  # NOTE(tjhance):
  # supports short-circuiting
  # without short-circuiting jif is unnecessary
  # are there performance issues?
  def jand(self, l, r): # inputs are functions
    left = l()
    if not isinstance(left, FExpr):
      return left and r()
    return self.jif(left, r, lambda:left)

  def jor(self, l, r): # inputs are functions
    left = l()
    if not isinstance(left, FExpr):
      return left or r()
    return self.jif(left, lambda:left, r)

  # this one is more straightforward
  # just takes an expression
  def jnot(self, f):
    if isinstance(f, FExpr):
      return Not(f)
    else:
      return not f

  def jassign(self, old, new):
    res = new
    for (var, val) in self.pathenv.conditions:
      if val:
        res = Facet(var, res, old)
      else:
        res = Facet(var, old, res)
    return res

  def jhasElt(self, lst, f):
    acc = False
    # Short circuits.
    for elt in lst:
      isElt = f(elt) # TODO: This should eventually be japply of f to elt.
      if isinstance(isElt, FExpr):
        acc = self.jor(lambda: isElt, lambda: acc)
      else:
        if isElt:
          return True
    return acc 
