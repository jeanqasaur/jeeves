# NOTE(JY): Importing JeevesLib for the write policy environment instance.
# Is there a better way to do this?
from macropy.case_classes import macros, enum
import JeevesLib
from AST import And, Facet, FExpr
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
      r = self.inputWP(self.v)(writer)
      if isinstance(r, FExpr):
        r = JeevesLib.concretize(writeCtxt, partialEval(r))
      if r:
        return UpdateResult.Success
      else:
        return UpdateResult.Failure
    else:
      return UpdateResult.Success
  def applyOutputWP(self, writer):
    if self.outputWP:
      try:
        r = self.outputWP(self.v)(writer)(Undefined)
        if isinstance(r, FExpr):
          r = PartialEval(r)
        if r == True:
          return UpdateResult.Success
        elif r == False:
          return UpdateResult.Failure
        else:
          return UpdateResult.Unknown
      except Exception:
        return UpdateResult.Unknown
    else:
      return UpdateResult.Success

  def addWritePolicy(self, label, writer):
    if self.outputWP:
      return JeevesLib.jeevesState.writeenv.addWritePolicy(label
        , self.outputWP(self.v), writer)
    else:
      return label

  # TODO: store the current writer with the Jeeves environment?
  def update(self, writer, writeCtxt, vNew):
    # For each variable, make a copy of it and add policies.
    def mkFacetTree(pathvars, high, low):
      if pathvars:
        (bv, isPos) = pathvars.pop()
        bvNew = self.addWritePolicy(bv, writer)
        
        lv = JeevesLib.mkLabel(bv.name)
        JeevesLib.jeevesState.writeenv.mapPrimaryContext(lv, writer)
        newFacet = mkFacetTree(pathvars, high, low)
        if isPos:
          JeevesLib.restrict(lv, lambda ic: lv)
          return Facet(bvNew, newFacet, low)
        else:
          JeevesLib.restrict(lv, lambda ic: not lv)
          return Facet(bvNew, low, newFacet)
      # If there are not path variables, then return the high facet.
      else:
        return high

    # First we try to apply the input write policy. If it for sure didn't work,
    # then we return the old value.
    if self.applyInputWP(writer, writeCtxt) == UpdateResult.Failure:
      return UpdateResult.Failure
    else:
      if not self.outputWP:
        self.v = vNew
        return UpdateResult.Success
      if self.outputWP:
        success = self.applyOutputWP(writer)
        if success == UpdateResult.Failure:
          return success
        else:
          # Create a new label and map it to the resulting confidentiality
          # policy in the confidentiality policy environment.
          wvar = JeevesLib.mkLabel() # TODO: Label this?
          vOld = self.v
          if success == UpdateResult.Unknown:
            JeevesLib.restrict(wvar
              , lambda octxt: self.outputWP(vOld)(writer)(octxt))

          if isinstance(vNew, FExpr):
            vNewRemapped = vNew.remapLabels(self.outputWP(vOld), writer)
          else:
            vNewRemapped = vNew

          # Create a faceted value < wvar ? vNew' : vOld >, where vNew' has the
          # write-associated labels remapped to take into account the new
          # writer. Add the path conditions.
          JeevesLib.jeevesState.pathenv.push(wvar, True)
          rPC = mkFacetTree(JeevesLib.jeevesState.pathenv.getEnv().items()
                  , vNewRemapped, vOld)
          JeevesLib.jeevesState.pathenv.pop()

          # Map the context down here to avoid overhead in making a new label
          # twice.
          JeevesLib.jeevesState.writeenv.mapPrimaryContext(wvar, writer)

          self.v = rPC
          return success
