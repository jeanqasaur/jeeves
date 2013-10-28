# NOTE(JY): Importing JeevesLib for the write policy environment instance.
# Is there a better way to do this?
from macropy.case_classes import macros, enum
import JeevesLib

@enum
class UpdateResult:
  Success, Unknown, Failure

class ProtectedRef:
  # TODO: Find nice ways of supplying defaults for inputWritePolicy and
  # outputWritePolicy?
  def __init__(self, v, inputWP, inputDeclassWP, outputWP):
    self.v = v
    self.inputWP = inputWP
    self.inputDeclassWP = inputDeclassWP
    self.outputWP = outputWP

  # TODO: store the current writer with the Jeeves environment?
  def update(self, writer, writeCtxt, vNew):
    # TODO: Create a new facet with the new value and the old value.
    # TODO: Walk over the resulting facet tree to make sure the current writer
    # is associated with labels associated with writes.
    # TODO: Update write policy environment to map all of the labels.
    return NotImplemented
