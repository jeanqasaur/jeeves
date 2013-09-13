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
  
  def vars(): return vars

  # TODO: Need to figure out a way to thread the environment through eval so
  # we don't have to pass the argument explicitly. We also want to make sure
  # that we're using the correct environment though... Do we have to use some
  # sort of global? :(
  @abstractmethod
  def eval(env): return NotImplemented
  @abstractmethod
  def __eq__(self, other): return NotImplemented

'''
Facets.
NOTE(JY): I think we don't have to have specialized facets anymore because we
don't have to deal with such a strict type system. One reason we might not be
able to do this is if we have to specialize execution of facets by checking
the type of the facet...
'''
class Facet(FExpr):
  def __init__(cond, thn, els):
    cond = cond
    thn = thn
    els = els

class Constant(FExpr):
  vars = set()
  def __init__(self, v):
    v = v
  def eval(env): v

'''
Binary expressions.
'''
class BinaryExpr(FExpr):
  def __init__(self, left, right):
    left = left
    right = right
  def vars(): left().vars().union(right.vars())
class UnaryExpr(FExpr):
  def __init__(self, sub):
    sub = sub

'''
Operators.
'''
class Eq(BinaryExpr):
  def eval(env):
    left().eval() == right().eval()
class And(BinaryExpr):
  def eval(env):
    left().eval() and right().eval()
class Or(BinaryExpr):
  def eval(env):
    left.eval() or right().eval()
class Not(UnaryExpr):
  def eval(env):
    not sub.eval()
# TODO: More operators here!


'''
Sensitive Boolean expressions.
NOTE(JY): I'm making the change Formula-> BoolExpr so that everything matches
better.
'''
class BoolExpr(FExpr):
  def __eq__(self, other): Eq(self, other)
  def constant(v): BoolVal(v)
  def default(): return NotImplemented
  def __and__(self, other): And(self, other)
  def __or__(self, other): Or(self, other)
  # TODO: Make this infix?
  def implies(self, other): Not(self) or other
  def iff(self, other): self == other
  def facet(self, thn, els): Facet(self, thn, els)
class BoolVal(BoolExpr, Constant):
  def __init__(self, v):
    v = v

'''
Integer expressions.
'''
class IntExpr(FExpr):
  __metaclass__ = ABCMeta
  # TODO: Put more stuff here!
