'''
This defines the abstract syntax tree for sensitive expressions.

Note(JY): An interesting thing is that we no longer need to define polymorphism
in types explicitly. We might be able to have a much cleaner implementation than
the Scala one!
'''
from abc import ABCMeta, abstractmethod
import operator
import JeevesGlobal
import z3

#TODO the type stuff

'''
Abstract class for sensitive expressions.
'''
class FExpr:
  __metaclass__ = ABCMeta
  
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

  # TODO bitwise operations? do we care?

  # do not need right-hand versions of the comparison operators
  def __eq__(l, r):
    return Eq(l, fexpr_cast(r))

  def __ne__(l, r): return Not(Eq(l, fexpr_cast(r)))

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

'''
Facets.
NOTE(JY): I think we don't have to have specialized facets anymore because we
don't have to deal with such a strict type system. One reason we might not be
able to do this is if we have to specialize execution of facets by checking
the type of the facet...
'''
class Facet(FExpr):
  def __init__(self, cond, thn, els):
    self.cond = cond
    self.thn = fexpr_cast(thn)
    self.els = fexpr_cast(els)

    # Note (TJH): idiomatic python does lots of automatic casts to bools,
    # especially to check if an integer is nonzero, for instance. We might
    # want to consider casting
    if self.cond.type != bool:
        raise TypeError("Condition on Facet should be a bool but is type %s."
                            % self.cond.type.__name__)

    # Note (TJH): Ordinary Python would of course allow these types to be
    # distinct, but that sounds pretty annoying to support on our end.
    if self.thn.type != self.els.type:
        raise TypeError("Condition on both sides of a Facet must have the "
                        "same type, they are %s and %s."
                        % (self.thn.type.__name__, self.els.type.__name__))

    self.type = self.thn.type

  def eval(self, env):
    return self.thn.eval(env) if self.cond.eval(env) else self.els.eval(env)

  def vars(self):
    return self.cond.vars().union(self.thn.vars()).union(self.els.vars())

  def z3Node(self):
    return z3.If(self.cond.z3Node(), self.thn.z3Node(), self.els.z3Node())

  def getChildren(self):
    return [self.cond, self.thn, self.els]
    
class Constant(FExpr):
  def __init__(self, v):
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

  def prettyPrint(self, indent):
    return indent + repr(self.v)

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

  def vars(self):
    return self.sub.vars()

  def getChildren(self):
    return [self.sub]

'''
Operators.
'''
class Add(BinaryExpr):
  opr = operator.add
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) + self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() + self.right.z3Node()

class Sub(BinaryExpr):
  opr = operator.sub
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) - self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() - self.right.z3Node()

class Mult(BinaryExpr):
  opr = operator.mul
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) * self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() * self.right.z3Node()

class Div(BinaryExpr):
  opr = operator.div
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) / self.right.eval(env)
  def z3Node(self):
    return NotImplemented

class Mod(BinaryExpr):
  opr = operator.mod
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) % self.right.eval(env)
  def z3Node(self):
    return NotImplemented

# Not sure if bitwise operations are supported by Z3?
class BitAnd(BinaryExpr):
  opr = operator.and_
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) & self.right.eval(env)
  def z3Node(self):
    return NotImplemented

class BitOr(BinaryExpr):
  opr = operator.or_
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) | self.right.eval(env)
  def z3Node(self):
    return NotImplemented

class LShift(BinaryExpr):
  opr = operator.ilshift
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) << self.right.eval(env)
  def z3Node(self):
    return NotImplemented

class RShift(BinaryExpr):
  opr = operator.irshift
  ret_type = int
  def eval(self, env):
    return self.left.eval(env) >> self.right.eval(env)
  def z3Node(self):
    return NotImplemented

# Boolean operations

class And(BinaryExpr):
  opr = operator.and_
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) and self.right.eval(env)
  def z3Node(self):
    return z3.And(self.left.z3Node(), self.right.z3Node())

class Or(BinaryExpr):
  opr = operator.or_
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) or self.right.eval(env)
  def z3Node(self):
    return z3.Or(self.left.z3Node(), self.right.z3Node())

class Not(UnaryExpr):
  opr = operator.not_
  ret_type = bool
  def eval(self, env):
    return not self.sub.eval(env)
  def z3Node(self):
    return z3.Not(self.sub.z3Node())

# Doesn't correspond to a Python operator but is useful
class Implies(BinaryExpr):
  opr = lambda x, y : (not x) or y
  ret_type = bool
  def eval(self, env):
    return (not self.left.eval(env)) or self.right.eval(env)
  def z3Node(self):
    return z3.Implies(self.left.z3Node(), self.right.z3Node())

# Comparison operations

class Eq(BinaryExpr):
  opr = operator.eq
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) == self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() == self.right.z3Node()

class Lt(BinaryExpr):
  opr = operator.lt
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) < self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() < self.right.z3Node()

class LtE(BinaryExpr):
  opr = operator.le
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) <= self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() <= self.right.z3Node()

class Gt(BinaryExpr):
  opr = operator.gt
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) > self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() > self.right.z3Node()

class GtE(BinaryExpr):
  opr = operator.ge
  ret_type = bool
  def eval(self, env):
    return self.left.eval(env) >= self.right.eval(env)
  def z3Node(self):
    return self.left.z3Node() >= self.right.z3Node()

# helper method
def fexpr_cast(a):
  if isinstance(a, FExpr):
    return a
  else:
    return Constant(a)
