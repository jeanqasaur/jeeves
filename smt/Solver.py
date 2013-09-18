'''
Defines the interface to solvers.
'''
from abc import ABCMeta, abstractmethod

# TODO: Define UnsatException and SolverException

class Solver:
  __metaclass__ = ABCMeta

  def __init__(self):
    pass

  @abstractmethod
  def check(): return NotImplemented
  @abstractmethod
  def eval(term): return NotImplemented
  @abstractmethod
  def solverAssert(s): return NotImplemented
  @abstractmethod
  def push(): return NotImplemented
  @abstractmethod
  def pop(): return NotImplemented
  @abstractmethod
  def reset(): return NotImplemented

  #TODO: Logging? Solver description?
