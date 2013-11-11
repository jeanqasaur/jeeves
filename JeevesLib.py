'''
This will define the code for the Jeeves library.
'''

# Import statements at bottom

class JeevesState:
    pass
jeevesState = JeevesState()

def init():
  jeevesState.varenv = VarEnv()
  jeevesState.pathenv = PathVars()
  jeevesState.policyenv = PolicyEnv()
  jeevesState.writeenv = WritePolicyEnv()

# NOTE(JY): We have to take care of the scoping somehow to make sure that
# we don't duplicate variables. One potential solution we can do, though, is
# to have a tight coupling with the solver where
def mkLabel(varName = ""):
  return jeevesState.policyenv.mkLabel(varName)

# NOTE(JY): Maybe we can just define a macro transformation here and interact
# directly with the environment.
# I think we can do this quite nicely by defining a mapping from our AST
# expressions to Z3 expressions and then directly adding those to the solver.
def restrict(varLabel, pred):
  # 1. Walk over the predicate AST and turn it into a Z3 formula.
  # 2. Add the formula (not pred) ==> (varLabel == false) to the constraint
  #    environment.

  # NOTE(JY): This should never be unsat...
  jeevesState.policyenv.restrict(varLabel, pred)

def mkSensitive(varLabel, vHigh, vLow):
  return Facet(varLabel, fexpr_cast(vHigh), fexpr_cast(vLow))

# TODO: Push a context, try setting things to high 
def concretize(ctxt, v):
  return jeevesState.policyenv.concretizeExp(ctxt, v)

def jif(cond, thn_fn, els_fn):
  condTrans = partialEval(fexpr_cast(cond))
  if condTrans.type != bool:
    raise TypeError("jif must take a boolean as a condition")
  return jif2(condTrans, thn_fn, els_fn)

def jif2(cond, thn_fn, els_fn):
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
    hasP = jeevesState.pathenv.hasPosVar(cond.cond)
    hasN = jeevesState.pathenv.hasNegVar(cond.cond)

    if not hasN:
      with PositiveVariable(cond.cond):
        thn = jif2(cond.thn, thn_fn, els_fn)
    if not hasP:
      with NegativeVariable(cond.cond):
        els = jif2(cond.els, thn_fn, els_fn)

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
def jand(l, r): # inputs are functions
  left = l()
  if not isinstance(left, FExpr):
    return left and r()
  return jif(left, r, lambda:left)

def jor(l, r): # inputs are functions
  left = l()
  if not isinstance(left, FExpr):
    return left or r()
  return jif(left, lambda:left, r)

# this one is more straightforward
# just takes an expression
def jnot(f):
  if isinstance(f, FExpr):
    return Not(f)
  else:
    return not f

def jassign(old, new):
  res = new
  for (var, val) in jeevesState.pathenv.conditions:
    if val:
      res = Facet(var, res, old)
    else:
      res = Facet(var, old, res)
  return res

def jhasElt(lst, f):
  acc = False
  # Short circuits.
  for elt in lst:
    isElt = f(elt) # TODO: This should eventually be japply of f to elt.
    if isinstance(isElt, FExpr):
      acc = jor(lambda: isElt, lambda: acc)
    else:
      if isElt:
        return True
  return acc 

def jhas(lst, v):
  return jhasElt(lst, lambda x: x == v)

class PositiveVariable:
  def __init__(self, var):
    self.var = var
  def __enter__(self):
    jeevesState.pathenv.push(self.var, True)
  def __exit__(self, type, value, traceback):
    jeevesState.pathenv.pop()

class NegativeVariable:
  def __init__(self, var):
    self.var = var
  def __enter__(self):
    jeevesState.pathenv.push(self.var, False)
  def __exit__(self, type, value, traceback):
    jeevesState.pathenv.pop()

def liftTuple(t):
  t = fexpr_cast(t)
  if isinstance(t, FObject):
    return t.v
  elif isinstance(t, Facet):
    a = liftTuple(t.thn)
    b = liftTuple(t.els)
    return tuple([Facet(t.cond, a1, b1) for (a1, b1) in zip(a, b)])
  else:
    raise TypeError("bad use of liftTuple")

class Namespace:
  def __init__(self, kw):
    self.__dict__.update(kw)

  def __setattr__(self, attr, value):
    self.__dict__[attr] = jassign(self.__dict__.get(attr, Unassigned()), value)

def jgetattr(obj, attr):
  if isinstance(obj, FExpr):
    return getattr(obj, attr)
  else:
    return getattr(obj, attr) if hasattr(obj, attr) else Unassigned()

def jgetitem(obj, item):
  try:
    return obj[item]
  except (KeyError, KeyError, TypeError) as e:
    return Unassigned()

def jmap(iterable, mapper):
  iterable = partialEval(fexpr_cast(iterable))
  return jmap2(iterable, mapper)
def jmap2(iterator, mapper):
  if isinstance(iterator, Facet):
    return jif(iterator.cond,
        lambda : jmap2(iterator.thn, mapper),
        lambda : jmap2(iterator.els, mapper))
  elif isinstance(iterator, FObject):
    return jmap2(iterator.v, mapper)
  elif isinstance(iterator, JList):
    return JList(jmap2(iterator.l, mapper))
  elif isinstance(iterator, list) or isinstance(iterator, tuple):
    return [mapper(item) for item in iterator]

def facetMapper(facet, fn):
  if isinstance(facet, Facet):
    return Facet(facet.cond, facetMapper(facet.thn, fn), facetMapper(facet.els, fn))
  elif isinstance(facet, Constant) or isinstance(facet, FObject):
    return fexpr_cast(fn(facet.v))

class JList:
  def __init__(self, l):
    self.l = fexpr_cast(l)
  def __getitem__(self, i):
    return self.l[i]
  def __setitem__(self, i, val):
    self.l[i] = jassign(self.l[i], val)

  def __len__(self):
    return self.l.__len__()
  def __iter__(self):
    return self.l.__iter__()

  def append(self, val):
    l2 = facetMapper(self.l, list) #deep copy
    l2.append(val)
    self.l = jassign(self.l, l2)

from env.VarEnv import VarEnv
from env.PolicyEnv import PolicyEnv
from env.PathVars import PathVars
from env.WritePolicyEnv import WritePolicyEnv
from smt.Z3 import Z3
from fast.AST import Facet, fexpr_cast, Constant, Var, Not, FExpr, Unassigned, FObject
from eval.Eval import partialEval
import copy
