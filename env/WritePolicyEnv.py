import JeevesLib

# import fast.AST
# from collections import defaultdict

class WritePolicyEnv:
  def __init__(self):
    self.writers = {}

  def mapPrimaryContext(self, ivar, ctxt):
    self.writers[ivar] = ctxt

  # This function associates a new set of write policies with a label.
  def addWritePolicy(self, label, policy, newWriter):
    # If the label is associated with a writer, then associate it with the
    # new write policies.
    if self.writers.has_key(label):
      ictxt = self.writers[label]

      # Make a new label mapped to the same writer.
      newLabel = JeevesLib.mkLabel(label.name)
      self.mapPrimaryContext(newLabel, ictxt)

      # Associate the new policies with this new label.
      JeevesLib.restrict(newLabel
        , lambda oc:
            JeevesLib.jand(lambda: label
              , lambda: JeevesLib.jand(
                  lambda: policy(ictxt)(oc)
                , lambda: policy(newWriter)(oc))))
      return newLabel
    # Otherwise return the label as is.
    else:
      return label
