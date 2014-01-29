'''
This will define the code for the Jeeves library.
'''

from env.VarEnv import VarEnv
from env.PolicyEnv import PolicyEnv
from env.PathVars import PathVars
from env.WritePolicyEnv import WritePolicyEnv
from smt.Z3 import Z3
from fast.AST import Facet, fexpr_cast, Constant, Var, Not, FExpr, Unassigned, FObject, jeevesState
from eval.Eval import partialEval
import copy

def init():
  jeevesState.varenv = VarEnv()
  jeevesState.pathenv = PathVars()
  jeevesState.policyenv = PolicyEnv()
  jeevesState.writeenv = WritePolicyEnv()

def supports_jeeves(f):
  f.__jeeves = 0
  return f

@supports_jeeves
def mkLabel(varName = ""):
  return jeevesState.policyenv.mkLabel(varName)

@supports_jeeves
def restrict(varLabel, pred):
  jeevesState.policyenv.restrict(varLabel, pred)

@supports_jeeves
def mkSensitive(varLabel, vHigh, vLow):
  return Facet(varLabel, fexpr_cast(vHigh), fexpr_cast(vLow))

@supports_jeeves
def concretize(ctxt, v):
  return jeevesState.policyenv.concretizeExp(ctxt, v, jeevesState.pathenv.getEnv())

@supports_jeeves
def jif(cond, thn_fn, els_fn):
  condTrans = partialEval(fexpr_cast(cond), jeevesState.pathenv.getEnv())
  if condTrans.type != bool:
    raise TypeError("jif must take a boolean as a condition")
  return jif2(condTrans, thn_fn, els_fn)

def jif2(cond, thn_fn, els_fn):
  if isinstance(cond, Constant):
    return thn_fn() if cond.v else els_fn()

  elif isinstance(cond, Facet):
    if not isinstance(cond.cond, Var):
      raise TypeError("facet conditional is of type %s"
                      % cond.cond.__class__.__name__)

    with PositiveVariable(cond.cond):
      thn = jif2(cond.thn, thn_fn, els_fn)
    with NegativeVariable(cond.cond):
      els = jif2(cond.els, thn_fn, els_fn)

    return Facet(cond.cond, thn, els)

  else:
    raise TypeError("jif condition must be a constant or a var")

# NOTE(tjhance):
# supports short-circuiting
# without short-circuiting jif is unnecessary
# are there performance issues?
@supports_jeeves
def jand(l, r): # inputs are functions
  left = l()
  if not isinstance(left, FExpr):
    return left and r()
  return jif(left, r, lambda:left)

@supports_jeeves
def jor(l, r): # inputs are functions
  left = l()
  if not isinstance(left, FExpr):
    return left or r()
  return jif(left, lambda:left, r)

# this one is more straightforward
# just takes an expression
@supports_jeeves
def jnot(f):
  if isinstance(f, FExpr):
    return Not(f)
  else:
    return not f

@supports_jeeves
def jassign(old, new):
  res = new
  for vs in jeevesState.pathenv.conditions:
    (var, val) = (vs.var, vs.val)
    if val:
      res = Facet(var, res, old)
    else:
      res = Facet(var, old, res)
  return res

'''
@supports_jeeves
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

@supports_jeeves
def jhas(lst, v):
  return jhasElt(lst, lambda x: x == v)
'''

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
  def __init__(self, kw, funcname):
    self.__dict__.update(kw)
    self.__dict__['_jeeves_funcname'] = funcname

  def __setattr__(self, attr, value):
    self.__dict__[attr] = jassign(self.__dict__.get(attr, Unassigned("variable '%s' in %s" % (attr, self._jeeves_funcname))), value)

@supports_jeeves
def jgetattr(obj, attr):
  if isinstance(obj, FExpr):
    return getattr(obj, attr)
  else:
    return getattr(obj, attr) if hasattr(obj, attr) else Unassigned("attribute '%s'" % attr)

@supports_jeeves
def jgetitem(obj, item):
  try:
    return obj[item]
  except (KeyError, KeyError, TypeError) as e:
    return Unassigned("item '%s'" % attr)

@supports_jeeves
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

def facetMapper(facet, fn, wrapper=fexpr_cast):
  if isinstance(facet, Facet):
    return Facet(facet.cond, facetMapper(facet.thn, fn), facetMapper(facet.els, fn))
  elif isinstance(facet, Constant) or isinstance(facet, FObject):
    return wrapper(fn(facet.v))

class JList:
  def __init__(self, l):
    self.l = l if isinstance(l, FExpr) else FObject(l)
  def __getitem__(self, i):
    return self.l[i]
  def __setitem__(self, i, val):
    self.l[i] = jassign(self.l[i], val)

  def __len__(self):
    return self.l.__len__()
  def __iter__(self):
    return self.l.__iter__()

  def append(self, val):
    l2 = facetMapper(self.l, list, FObject) #deep copy
    l2.append(val)
    self.l = jassign(self.l, l2)

@supports_jeeves
def jfun(f, *args, **kw):
  if hasattr(f, '__jeeves'):
    return f(*args, **kw)
  else:
    env = jeevesState.pathenv.getEnv()
    if len(args) > 0:
      return jfun2(f, args, kw, 0, partialEval(fexpr_cast(args[0]), env), [])
    else:
      it = kw.__iter__()
      try:
        fst = next(it)
      except StopIteration:
        return fexpr_cast(f())
      return jfun3(f, kw, it, fst, partialEval(fexpr_cast(kw[fst]), env), (), {})

def jfun2(f, args, kw, i, arg, args_concrete):
  if isinstance(arg, Constant) or isinstance(arg, FObject):
    env = jeevesState.pathenv.getEnv()
    if i < len(args) - 1:
      return jfun2(f, args, kw, i+1, partialEval(fexpr_cast(args[i+1]), env), tuple(list(args_concrete) + [arg.v]))
    else:
      it = kw.__iter__()
      try:
        fst = next(it)
      except StopIteration:
        return fexpr_cast(f(*tuple(list(args_concrete) + [arg.v])))
      return jfun3(f, kw, it, fst, partialEval(fexpr_cast(kw[fst]), env), tuple(list(args_concrete) + [arg.v]), {})
  else:
    with PositiveVariable(arg.cond):
      thn = jfun2(f, args, kw, i, arg.thn, args_concrete)
    with NegativeVariable(arg.cond):
      els = jfun2(f, args, kw, i, arg.els, args_concrete)
    return Facet(arg.cond, thn, els)

def jfun3(f, kw, it, key, val, args_concrete, kw_concrete):
  if isinstance(val, Constant) or isinstance(val, FObject):
    kw_c = dict(kw_concrete)
    kw_c[key] = val.v
    try:
      next_key = next(it)
    except StopIteration:
      return fexpr_cast(f(*args_concrete, **kw_c))
    env = jeevesState.pathenv.getEnv()
    return jfun3(f, kw, it, next_key, partialEval(fexpr_cast(kw[next_key]), env), args_concrete, kw_c)
  else:
    with PositiveVariable(val.cond):
      thn = jfun3(f, kw, it, key, val.thn, args_concrete, kw_concrete)
    with NegativeVariable(val.cond):
      els = jfun3(f, kw, it, key, val.els, args_concrete, kw_concrete)
    return Facet(arg.cond, thn, els)

from jlib.JContainer import *
