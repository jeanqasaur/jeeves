'''
This defines the abstract syntax tree for sensitive expressions.

Note(JY): An interesting thing is that we no longer need to define polymorphism
in types explicitly. We might be able to have a much cleaner implementation than
the Scala one!
'''
from abc import ABCMeta, abstractmethod

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
  @abstractmethod
  def eval(self, env):
    return NotImplemented

  @abstractmethod
  def __eq__(self, other):
    return NotImplemented

'''
Sensitive Boolean expressions.
NOTE(JY): I'm making the change Formula-> BoolExpr so that everything matches
better.
'''
class BoolExpr(FExpr):
  __metaclass__ = ABCMeta

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
class IntExpr(FExpr):
  __metaclass__ = ABCMeta

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

  def __ne__(l, r):
    return Not(Eq(l, fexpr_cast(r)))

  def __lt__(l, r):
    return Lt(l, fexpr_cast(r))

  def __gt__(l, r):
    return Gt(l, fexpr_cast(r))

  def __le__(l, r):
    return LtE(l, fexpr_cast(r))

  def __ge__(l, r):
    return GtE(l, fexpr_cast(r))

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

  def eval(self, env):
    raise NotImplementedError

class IntFacet(Facet, IntExpr):
    pass

class BoolFacet(Facet, BoolExpr):
    pass

class Constant(FExpr):
  def __init__(self, v):
    self.v = v

  def eval(self, env):
    return v

  def vars(self):
    return set()

class IntVal(IntExpr, Constant):
  def __init__(self, v):
    self.v = v
  def eval(self, env):
    return self.v

class BoolVal(BoolExpr, Constant):
  def __init__(self, v):
    self.v = v
  def eval(self, env):
    return self.v

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
class Add(BinaryExpr, IntExpr):
    def eval(self, env):
        return self.left.eval(env) + self.right.eval(env)

class Sub(BinaryExpr, IntExpr):
    def eval(self, env):
        return self.left.eval(env) - self.right.eval(env)

class Mult(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) * self.right.eval(env)

class Div(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) / self.right.eval(env)

class Mod(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) % self.right.eval(env)

# Not sure if bitwise operations are supported by Z3?
class BitAnd(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) & self.right.eval(env)

class BitOr(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) | self.right.eval(env)

class LShift(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) << self.right.eval(env)

class RShift(BinaryExpr, IntExpr):
  def eval(self, env):
    return self.left.eval(env) >> self.right.eval(env)

# Boolean operations

class And(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) and self.right.eval(env)

class Or(BinaryExpr, BoolExpr):
  def eval(env):
    return self.left.eval(env) or self.right.eval(env)

class Not(UnaryExpr, BoolExpr):
  def eval(self, env):
    return not self.sub.eval(env)

# Comparison operations

class Eq(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) == self.right.eval(env)

class Lt(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) < self.right.eval(env)

class LtE(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) >= self.right.eval(env)

class Gt(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) > self.right.eval(env)

class GtE(BinaryExpr, BoolExpr):
  def eval(self, env):
    return self.left.eval(env) >= self.right.eval(env)

def fexpr_cast(a):
    if isinstance(a, FExpr):
        return a
    elif isinstance(a, int):
        return IntVal(a)
    elif isinstance(a, bool):
        return BoolVal(a)
    else:
        raise TypeError("Bad type for FExpr cast")
