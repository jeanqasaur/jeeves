'''
This defines the abstract syntax tree for sensitive expressions.

Note(JY): An interesting thing is that we no longer need to define polymorphism
in types explicitly. We might be able to have a much cleaner implementation than
the Scala one!
'''
from abc import ABCMeta, abstractmethod
import operator
import JeevesGlobal

class Label:
  def __init__(name=None):
    self.name = name

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
  def eval(self):
    return NotImplemented

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
    Var.counter += 1

  def eval(self):
    if JeevesGlobal.jeevesLib.pathenv.hasPosVar(self):
      return True
    elif JeevesGlobal.jeevesLib.pathenv.hasNegVar(self):
      return False
    else:
      raise CannotEvalException("Variable %s is not in path environment" % self)

  def __str__(self):
    return self.name

  def vars(self):
    return {self}

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

  def eval(self):
    if JeevesGlobal.jeevesLib.pathenv.hasPosVar(self.cond):
      return self.thn.eval()
    elif JeevesGlobal.jeevesLib.pathenv.hasNegVar(self.cond):
      return self.els.eval()

  def vars(self):
    return self.cond.vars().union(self.thn.vars()).union(self.els.vars())
    

class Constant(FExpr):
  def __init__(self, v):
    self.v = v

  def eval(self):
    return self.v

  def vars(self):
    return set()

'''
Binary expressions.
'''
class BinaryExpr(FExpr):
  def __init__(self, left, right):
    self.left = left
    self.right = right

  def vars(self):
    return self.left.vars().union(self.right.vars())

class UnaryExpr(FExpr):
  def __init__(self, sub):
    self.sub = sub

  def vars(self):
    return self.sub.vars()

'''
Operators.
'''
class Add(BinaryExpr):
  opr = operator.add
  def eval(self):
    return self.left.eval() + self.right.eval()

class Sub(BinaryExpr):
  opr = operator.sub
  def eval(self):
    return self.left.eval() - self.right.eval()

class Mult(BinaryExpr):
  opr = operator.mul
  def eval(self):
    return self.left.eval() * self.right.eval()

class Div(BinaryExpr):
  opr = operator.div
  def eval(self):
    return self.left.eval() / self.right.eval()

class Mod(BinaryExpr):
  opr = operator.mod
  def eval(self):
    return self.left.eval() % self.right.eval()

# Not sure if bitwise operations are supported by Z3?
class BitAnd(BinaryExpr):
  opr = operator.and_
  def eval(self):
    return self.left.eval() & self.right.eval()

class BitOr(BinaryExpr):
  opr = operator.or_
  def eval(self):
    return self.left.eval() | self.right.eval()

class LShift(BinaryExpr):
  opr = operator.ilshift
  def eval(self):
    return self.left.eval() << self.right.eval()

class RShift(BinaryExpr):
  opr = operator.irshift
  def eval(self):
    return self.left.eval() >> self.right.eval()

# Boolean operations

class And(BinaryExpr):
  opr = operator.and_
  def eval(self):
    return self.left.eval() and self.right.eval()

class Or(BinaryExpr):
  opr = operator.or_
  def eval():
    return self.left.eval() or self.right.eval()

class Not(UnaryExpr):
  opr = operator.not_
  def eval(self):
    return not self.sub.eval()

# Comparison operations

class Eq(BinaryExpr):
  opr = operator.eq
  def eval(self):
    return self.left.eval() == self.right.eval()

class Lt(BinaryExpr):
  opr = operator.lt
  def eval(self):
    return self.left.eval() < self.right.eval()

class LtE(BinaryExpr):
  opr = operator.le
  def eval(self):
    return self.left.eval() <= self.right.eval()

class Gt(BinaryExpr):
  opr = operator.gt
  def eval(self):
    return self.left.eval() > self.right.eval()

class GtE(BinaryExpr):
  opr = operator.ge
  def eval(self):
    return self.left.eval() >= self.right.eval()

# helper method
def fexpr_cast(a):
  if isinstance(a, FExpr):
    return a
  else:
    return Constant(a)
