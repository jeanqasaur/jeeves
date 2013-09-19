'''
Defines the interface to solvers.
'''
from abc import ABCMeta, abstractmethod
from macropy.case_classes import macros, case

# TODO: Define UnsatException and SolverException

class Solver:
  __metaclass__ = ABCMeta

  @case
  class Sat(): pass

  @case
  class Unsat(): pass

  @case
  class Unknown(): pass

  def __init__(self):
    pass

  @abstractmethod
  def check(self): return Unknown
  @abstractmethod
  def eval(self, term): return NotImplemented
  @abstractmethod
  def solverAssert(self, s): return NotImplemented
  @abstractmethod
  def push(self): return NotImplemented
  @abstractmethod
  def pop(self): return NotImplemented
  @abstractmethod
  def reset(): return NotImplemented

  #TODO: Logging? Solver description?
