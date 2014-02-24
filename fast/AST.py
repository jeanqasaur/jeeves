'''
This defines the abstract syntax tree for sensitive expressions.

Note(JY): An interesting thing is that we no longer need to define polymorphism
in types explicitly. We might be able to have a much cleaner implementation than
the Scala one!
'''
from abc import ABCMeta, abstractmethod
import operator
import z3
import JeevesLib
import traceback

class JeevesState:
  pass
jeevesState = JeevesState()

'''
Abstract class for sensitive expressions.
'''
class FExpr:
  __metaclass__ = ABCMeta
  
  @abstractmethod
  def vars(self):
    return NotImplemented

  # TODO: Need to figure out a way to thread the environment through eval so
  # we don't have to pass the argument explicitly. We also want to make sure
  # that we're using the correct environment though... Do we have to use some
  # sort of global? :(
  # TJH: going to just assume it's a global for now, so we don't have to
  # pass it through
  @abstractmethod
  def eval(self, env):
    return NotImplemented

  @abstractmethod
  def z3Node(self):
    return NotImplemented

  @abstractmethod
  def getChildren(self):
    return NotImplemented

  # Return a version of yourself with the write-associated labels remapped to
  # point to the new policy in addition to the previous policies.
  @abstractmethod
  def remapLabels(self, policy, writer):
    return NotImplemented

  def prettyPrint(self, indent=""):
    return "%s%s\n%s" % (indent, type(self).__name__,
      "\n".join(child.prettyPrint(indent + "  ")
                for child in self.getChildren()))

  '''
  Sensitive Boolean expressions.
  NOTE(JY): I'm making the change Formula-> BoolExpr so that everything matches
  better.
  '''

  def __eq__(l, r):
    return Eq(l, fexpr_cast(r))

  def __ne__(l, r):
    return Not(Eq(l, fexpr_cast(r)))
    
  # The & operator
  def __and__(l, r):
    return And(l, fexpr_cast(r))
  def __rand__(r, l):
    return And(fexpr_cast(l), r)

  # The | operator
  def __or__(l, r):
    return Or(l, fexpr_cast(r))
  def __ror__(r, l):
    return Or(fexpr_cast(l), r)

  #def constant(v): BoolVal(v)
  #def default(): return NotImplemented
  ## TODO: Make this infix?
  #def implies(self, other): Not(self) or other
  #def iff(self, other): self == other
  #def facet(self, thn, els): Facet(self, thn, els)

  '''
  Integer expressions.
  '''
  def __add__(l, r):
    return Add(l, fexpr_cast(r))
  def __radd__(r, l):
    return Add(fexpr_cast(l), r)

  def __sub__(l, r):
    return Sub(l, fexpr_cast(r))
  def __rsub__(r, l):
    return Sub(fexpr_cast(l), r)

  def __mul__(l, r):
    return Mult(l, fexpr_cast(r))
  def __rmul__(r, l):
    return Mult(fexpr_cast(l), r)

  def __div__(l, r):
    return Div(l, fexpr_cast(r))
  def __rdiv__(r, l):
    return Div(fexpr_cast(l), r)

  def __mod__(l, r):
    return Mod(l, fexpr_cast(r))
  def __rmod__(r, l):
    return Mod(fexpr_cast(l), r)

  def __abs__(v):
    if isinstance(v, FExpr):
      return JeevesLib.jif(v > 0, lambda:v, lambda:0 - v)
    return abs(v)

  # TODO bitwise operations? do we care?

  def __lt__(l, r):
    return Lt(l, fexpr_cast(r))

  def __gt__(l, r):
    return Gt(l, fexpr_cast(r))

  def __le__(l, r):
    return LtE(l, fexpr_cast(r))

  def __ge__(l, r):
    return GtE(l, fexpr_cast(r))

class CannotEvalException(Exception):
  pass

def get_var_by_name(var_name):
  v = Var()
  v.name = var_name
  return v

class Var(FExpr):
  counter = 0

  def __init__(self, name=None):
    if name:
      self.name = "v%d_%s" % (Var.counter, name)
    else:
      self.name = "v%d" % Var.counter
    self.type = bool
    Var.counter += 1

  def eval(self, env):
    try:
      return env[self]
    except IndexError:
      raise CannotEvalException("Variable %s is not in path environment" % self)

  def remapLabels(self, policy, writer):
    return self

  def __str__(self):
    return self.name

  def vars(self):
    return {self}

  def z3Node(self):
    return z3.Bool(self.name)

  def getChildren(self):
    return []

  def prettyPrint(self, indent=""):
    return indent + self.name

# helper methods for faceted __setattr__
def get_objs_in_faceted_obj(f, d, env):
  if isinstance(f, Facet):
    if f.cond.name in env:
      if env[f.cond.name]:
        get_objs_in_faceted_obj(f.thn, d, env)
      else:
        get_objs_in_faceted_obj(f.els, d, env)
    else:
      get_objs_in_faceted_obj(f.thn, d, env)
      get_objs_in_faceted_obj(f.els, d, env)
  elif isinstance(f, FObject):
    d[id(f.v)] = f.v
  else:
    raise TypeError("wow such error: attribute access for non-object type; %s"
            % f.__class__.__name__)

def replace_obj_attributes(f, obj, oldvalue, newvalue, env):
  if isinstance(f, Facet):
    if f.cond.name in env:
      if env[f.cond.name]:
        return replace_obj_attributes(f.thn, obj, oldvalue, newvalue, env)
      else:
        return replace_obj_attributes(f.els, obj, oldvalue, newvalue, env)
    else:
      return Facet(f.cond,
        replace_obj_attributes(f.thn, obj, oldvalue, newvalue, env),
        replace_obj_attributes(f.els, obj, oldvalue, newvalue, env))
  elif f.v is obj:
    return newvalue
  else:
    return oldvalue

'''
Facets.
NOTE(JY): I think we don't have to have specialized facets anymore because we
don't have to deal with such a strict type system. One reason we might not be
able to do this is if we have to specialize execution of facets by checking
the type of the facet...
'''
class Facet(FExpr):
  def __init__(self, cond, thn, els):
    assert isinstance(cond, Var)

    self.__dict__['cond'] = cond
    self.__dict__['thn'] = fexpr_cast(thn)
    self.__dict__['els'] = fexpr_cast(els)

    # Note (TJH): idiomatic python does lots of automatic casts to bools,
    # especially to check if an integer is nonzero, for instance. We might
    # want to consider casting
    if self.cond.type != bool:
        raise TypeError("Condition on Facet should be a bool but is type %s."
                            % self.cond.type.__name__)

    # Note (TJH): Ordinary Python would of course allow these types to be
    # distinct, but that sounds pretty annoying to support on our end.
    # TODO: Unassigned makes things super-awkward, we need to figure that out.
    # For now, just ignore them.
    #if (self.thn.type != None and self.els.type != None and
    #        self.thn.type != self.els.type):
    #    raise TypeError("Condition on both sides of a Facet must have the "
    #                    "same type, they are %s and %s."
    #                    % (self.thn.type.__name__, self.els.type.__name__))

    self.__dict__['type'] = self.thn.type or self.els.type

  def eval(self, env):
    return self.thn.eval(env) if self.cond.eval(env) else self.els.eval(env)

  def vars(self):
    return self.cond.vars().union(self.thn.vars()).union(self.els.vars())

  def z3Node(self):
    return z3.If(self.cond.z3Node(), self.thn.z3Node(), self.els.z3Node())

  def getChildren(self):
    return [self.cond, self.thn, self.els]

  def remapLabels(self, policy, writer):
    if isinstance(self.cond, Var):
      newCond = jeevesState.writeenv.addWritePolicy(
                  self.cond, policy, writer)
    else:
      newCond = self.cond.remapLabels(policy, writer)
    return Facet(newCond
      , self.thn.remapLabels(policy, writer)
      , self.els.remapLabels(policy, writer))

  def prettyPrint(self, indent=""):
    return "< " + self.cond.prettyPrint() + " ? " + self.thn.prettyPrint() + " : " + self.els.prettyPrint() + " >"
  def __str__(self):
    return self.prettyPrint()


  def __call__(self, *args, **kw):
    return JeevesLib.jif(self.cond,
        lambda:self.thn(*args, **kw), lambda:self.els(*args, **kw))

  # called whenever an attribute that does not exist is accessed
  def __getattr__(self, attribute):
    return Facet(self.cond,
      getattr(self.thn, attribute),
      getattr(self.els, attribute))

  def __setattr__(self, attribute, value):
    if attribute in self.__dict__:
      self.__dict__[attribute] = value
    else:
      env = jeevesState.pathenv.getEnv()
      value = fexpr_cast(value)
      objs = {}
      get_objs_in_faceted_obj(self, objs, env)
      for _, obj in objs.iteritems():
        t = replace_obj_attributes(self, obj, getattr(obj, attribute), value, env)
        setattr(obj, attribute, t)

  def __getitem__(self, attribute):
    return Facet(self.cond,
      self.thn[attribute],
      self.els[attribute])

  def __setitem__(self, attribute, value):
    env = jeevesState.pathenv.getEnv()
    value = fexpr_cast(value)
    objs = {}
    get_objs_in_faceted_obj(self, objs, env)
    for _, obj in objs.iteritems():
      t = replace_obj_attributes(self, obj, obj[attribute], value, env)
      obj[attribute] = t

  def __eq__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn == other,
                                                   lambda : self.els == other)
    else:
      return Eq(self, other)
  def __ne__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn != other,
                                                   lambda : self.els != other)
    else:
      return Not(Eq(self, other))
  def __lt__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn < other,
                                                   lambda : self.els < other)
    else:
      return Lt(self, other)
  def __gt__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn > other,
                                                   lambda : self.els > other)
    else:
      return Gt(self, other)
  def __le__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn <= other,
                                                   lambda : self.els <= other)
    else:
      return LtE(self, other)
  def __ge__(self, other):
    other = fexpr_cast(other)
    if self.type == object or other.type == object:
      return JeevesLib.jif(self.cond, lambda : self.thn >= other,
                                                   lambda : self.els >= other)
    else:
      return GtE(self, other)

  def __len__(self):
    if self.type == object:
      return JeevesLib.jif(self.cond, self.thn.__len__, self.els.__len__)
    else:
      raise TypeError("cannot take len of non-object; type %s" % self.type.__name__)

class Constant(FExpr):
  def __init__(self, v):
    assert not isinstance(v, FExpr)
    self.v = v
    self.type = type(v)

  def eval(self, env):
    return self.v

  def vars(self):
    return set()

  def z3Node(self):
    return self.v

  def getChildren(self):
    return []

  def remapLabels(self, policy, writer):
    return self

  def prettyPrint(self, indent=""):
    return indent + "const:" + repr(self.v)

  def __call__(self, *args, **kw):
    return self.v(*args, **kw)

'''
Binary expressions.
'''
class BinaryExpr(FExpr):
  def __init__(self, left, right):
    self.left = left
    self.right = right
    self.type = self.ret_type

  def vars(self):
    return self.left.vars().union(self.right.vars())

  def getChildren(self):
    return [self.left, self.right]

class UnaryExpr(FExpr):
  def __init__(self, sub):
    self.sub = sub
    self.type = self.ret_type

  def vars(self):
    return self.sub.vars()

  def getChildren(self):
    return [self.sub]

'''
Operators.
'''
class Add(BinaryExpr):
  opr = staticmethod(operator.add)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) + self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() + self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Add(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Sub(BinaryExpr):
  opr = staticmethod(operator.sub)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) - self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() - self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Sub(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Mult(BinaryExpr):
  opr = staticmethod(operator.mul)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) * self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() * self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Mult(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Div(BinaryExpr):
  opr = staticmethod(operator.div)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) / self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return Div(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Mod(BinaryExpr):
  opr = staticmethod(operator.mod)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) % self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return Mod(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

# Not sure if bitwise operations are supported by Z3?
class BitAnd(BinaryExpr):
  opr = staticmethod(operator.and_)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) & self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return BitAnd(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class BitOr(BinaryExpr):
  opr = staticmethod(operator.or_)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) | self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return BitOr(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class LShift(BinaryExpr):
  opr = staticmethod(operator.ilshift)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) << self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return LShift(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class RShift(BinaryExpr):
  opr = staticmethod(operator.irshift)
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) >> self.right.eval(env)
  def z3Node(self):
    return NotImplemented
  def remapLabels(self, policy, writer):
    return RShift(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

# Boolean operations

class And(BinaryExpr):
  opr = staticmethod(operator.and_)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) and self.right.eval(env)
  def z3Node(self):
    return z3.And(self.left.z3Node(), self.right.z3Node())
  def remapLabels(self, policy, writer):
    return And(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Or(BinaryExpr):
  opr = staticmethod(operator.or_)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) or self.right.eval(env)
  def z3Node(self):
    return z3.Or(self.left.z3Node(), self.right.z3Node())
  def remapLabels(self, policy, writer):
    return Or(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Not(UnaryExpr):
  opr = staticmethod(operator.not_)
  ret_type = bool
  def eval(self, env):
    return not self.sub.eval(env)
  def z3Node(self):
    return z3.Not(self.sub.z3Node())
  def remapLabels(self, policy, writer):
    return Not(self.sub.remapLabels(policy, writer))

# Doesn't correspond to a Python operator but is useful
class Implies(BinaryExpr):
  opr = staticmethod(lambda x, y : (not x) or y)
  ret_type = bool
  def eval(self, env):
    return (not self.left.eval(env)) or self.right.eval(env)
  def z3Node(self):
    return z3.Implies(self.left.z3Node(), self.right.z3Node())
  def remapLabels(self, policy, writer):
    return Implies(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

# Comparison operations

class Eq(BinaryExpr):
  opr = staticmethod(operator.eq)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) == self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() == self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Eq(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Lt(BinaryExpr):
  opr = staticmethod(operator.lt)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) < self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() < self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Lt(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class LtE(BinaryExpr):
  opr = staticmethod(operator.le)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) <= self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() <= self.right.z3Node()
  def remapLabels(self, policy, writer):
    return LtE(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Gt(BinaryExpr):
  opr = staticmethod(operator.gt)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) > self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() > self.right.z3Node()
  def remapLabels(self, policy, writer):
    return Gt(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class GtE(BinaryExpr):
  opr = staticmethod(operator.ge)
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) >= self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() >= self.right.z3Node()
  def remapLabels(self, policy, writer):
    return GtE(
        self.left.remapLabels(policy, writer)
      , self.right.remapLabels(policy, writer))

class Unassigned(FExpr):
  def __init__(self, thing_not_found):
    self.type = None
    self.thing_not_found = thing_not_found
  def eval(self, env):
    raise self.getException()
  def z3Node(self):
    pass #TODO ?? what goes here
  def getChildren(self):
    return []
  def remapLabels(self, policy):
    return self
  def vars(self):
    return set()
  def remapLabels(self, policy, writer):
    return self
  def getException(self):
    return Exception("wow such error: %s does not exist." % (self.thing_not_found,))
  def __call__(self, *args, **kwargs):
    raise self.getException()

# TODO(TJH): figure out the correct implementation of this
def is_obj(o):
  return isinstance(o, list) or isinstance(o, tuple) or hasattr(o, '__dict__')

# helper method
def fexpr_cast(a):
  if isinstance(a, FExpr):
    return a
  elif isinstance(a, list):
    return FObject(JeevesLib.JList(a))
  elif is_obj(a):
    return FObject(a)
  else:
    return Constant(a)

class FObject(FExpr):
  def __init__(self, v):
    assert not isinstance(v, JeevesLib.Namespace)
    self.__dict__['v'] = v
    self.__dict__['type'] = object

  def eval(self, env):
    return self.v

  def vars(self):
    return set()

  def z3Node(self):
    return id(self)

  def getChildren(self):
    return []

  # TODO: Make sure this is right...
  def remapLabels(self, policy, writer):
    if isinstance(self.v, FExpr):
      return FObject(self.v.remapLabels(policy, writer))
    else:
      return self

  def __call__(self, *args, **kw):
    return self.v.__call__(*args, **kw)

  # called whenever an attribute that does not exist is accessed
  def __getattr__(self, attribute):
    if hasattr(self.v, attribute):
      return getattr(self.v, attribute)
    else:
      return Unassigned("attribute '%s'" % attribute)

  def __setattr__(self, attribute, val):
    if attribute in self.__dict__:
      self.__dict__[attribute] = val
    else:
      setattr(self.v, attribute, val)

  def __getitem__(self, item):
    try:
      return self.v[item]
    except (KeyError, IndexError, TypeError):
      return Unassigned("item '%s'" % item)

  def __setitem__(self, item, val):
    self.v[item] = val

  def __len__(self):
    return self.v.__len__()

  def __eq__(self, other): 
    try:
      f = getattr(self.v, '__eq__')
    except AttributeError:
      return Eq(self, fexpr_cast(other))
    return f(other)

  def __ne__(self, other):
    try:
      f = getattr(self.v, '__ne__')
    except AttributeError:
      return Not(Eq(self, fexpr_cast(other)))
    return f(other)

  def __lt__(self, other):
    try:
      f = getattr(self.v, '__lt__')
    except AttributeError:
      return Lt(self, fexpr_cast(other))
    return f(other)

  def __gt__(self, other):
    try:
      f = getattr(self.v, '__gt__')
    except AttributeError:
      return Gt(self, fexpr_cast(other))
    return f(other)

  def __le__(self, other):
    try:
      f = getattr(self.v, '__le__')
    except AttributeError:
      return LtE(self, fexpr_cast(other))
    return f(other)

  def __ge__(self, other):
    try:
      f = getattr(self.v, '__ge__')
    except AttributeError:
      return GtE(self, fexpr_cast(other))
    return f(other)

"""
  def __and__(l, r):
  def __rand__(r, l):
  def __or__(l, r):
  def __ror__(r, l):
  def __add__(l, r):
  def __radd__(r, l):
  def __sub__(l, r):
  def __rsub__(r, l):
  def __mul__(l, r):
  def __rmul__(r, l):
  def __div__(l, r):
  def __rdiv__(r, l):
  def __mod__(l, r):
  def __rmod__(r, l):
"""
