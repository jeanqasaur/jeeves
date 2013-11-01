# NOTE(JY): Importing JeevesLib for the write policy environment instance.
# Is there a better way to do this?
from macropy.case_classes import macros, enum
import JeevesLib
from AST import And
from eval.Eval import partialEval

@enum
class UpdateResult:
  Success, Unknown, Failure

class Undefined(Exception):
  pass

class ProtectedRef:
  # TODO: Find nice ways of supplying defaults for inputWritePolicy and
  # outputWritePolicy?
  def __init__(self, v, inputWP, outputWP):
    self.v = v
    self.inputWP = inputWP
    self.outputWP = outputWP

  def applyInputWP(self, writer, writeCtxt):
    if self.inputWP:
      if JeevesLib.concretize(writeCtxt, partialEval(self.inputWP(writer))):
        return UpdateResult.Success
      else:
        return UpdateResult.Failure
    else:
      return UpdateResult.Success
  def applyOutputWP(self, writer):
    return NotImplemented

  # TODO: store the current writer with the Jeeves environment?
  def update(self, writer, writeCtxt, vNew):
    # First we try to apply the input write policy. If it for sure didn't work,
    # then we return the old value.
    if self.applyInputWP(writer, writeCtxt) == UpdateResult.Success:
      return self.v
    else:
      # TODO: Create a new facet with the new value and the old value.
      # TODO: Walk over the resulting facet tree to make sure the current writer
      # is associated with labels associated with writes.
      # TODO: Update write policy environment to map all of the labels.
      return applyOutputWP(self, writer)
