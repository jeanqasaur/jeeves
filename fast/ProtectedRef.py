# NOTE(JY): Importing JeevesLib for the write policy environment instance.
# Is there a better way to do this?
from macropy.case_classes import macros, enum
import JeevesLib
from AST import And, Facet, FExpr, FObject
from eval.Eval import partialEval

@enum
class UpdateResult:
  Success, Unknown, Failure

class Undefined(Exception):
  pass
class PolicyError(Exception):
  pass

@JeevesLib.supports_jeeves
class ProtectedRef:
  # TODO: Find nice ways of supplying defaults for inputWritePolicy and
  # outputWritePolicy?
  @JeevesLib.supports_jeeves
  def __init__(self, v, inputWP, outputWP, trackImplicit=True):
    self.v = v

    if isinstance(inputWP, FExpr):
      if isinstance(inputWP, FObject):
        self.inputWP = inputWP.v
      else:
        raise PolicyError("Input write policy cannot be faceted.")
    else:
      self.inputWP = inputWP
    
    if isinstance(outputWP, FExpr):
      if isinstance(outputWP, FObject):
        self.outputWP = outputWP.v
      else:
        raise PolicyError("Output write policy cannot be faceted.")
    else:
      self.outputWP = outputWP

    self.trackImplicit = trackImplicit

  @JeevesLib.supports_jeeves
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

  @JeevesLib.supports_jeeves
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

  @JeevesLib.supports_jeeves
  def addWritePolicy(self, label, writer):
    if self.outputWP:
      return JeevesLib.jeevesState.writeenv.addWritePolicy(label
        , self.outputWP(self.v), writer)
    else:
      return label

  # TODO: store the current writer with the Jeeves environment?
  @JeevesLib.supports_jeeves
  def update(self, writer, writeCtxt, vNew):
    # For each variable, make a copy of it and add policies.
    def mkFacetTree(pathvars, high, low):
      if pathvars:
        #(bv, isPos) = pathvars.pop()
        vs = pathvars.pop()
        bv = vs.var
        isPos = vs.val
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
          return UpdateResult.Failure
        else:
          vOld = self.v
          if isinstance(vNew, FExpr):
            vNewRemapped = vNew.remapLabels(self.outputWP(vOld), writer)
          else:
            vNewRemapped = vNew
 
          if success == UpdateResult.Success and (not self.trackImplicit):
            self.v = vNewRemapped
            return UpdateResult.Success
          # In this case, success == UpdateResult.Unknown or self.trackImplicit
          # is True.
          else:
            # Create a new label and map it to the resulting confidentiality
            # policy in the confidentiality policy environment.
            wvar = JeevesLib.mkLabel() # TODO: Label this?
            if success == UpdateResult.Unknown:
              JeevesLib.restrict(wvar
                , lambda octxt: self.outputWP(vOld)(writer)(octxt))

            # Create a faceted value < wvar ? vNew' : vOld >, where vNew' has
            # the write-associated labels remapped to take into account the new
            # writer. Add the path conditions.
            JeevesLib.jeevesState.pathenv.push(wvar, True)
            rPC = mkFacetTree(list(JeevesLib.jeevesState.pathenv.conditions)
                    , vNewRemapped, vOld)
            JeevesLib.jeevesState.pathenv.pop()

            if self.trackImplicit:
              JeevesLib.jeevesState.writeenv.mapPrimaryContext(wvar, writer)

            self.v = rPC
            return success
