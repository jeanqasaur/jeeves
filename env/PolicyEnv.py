import JeevesGlobal
import fast.AST

class PolicyEnv:
  def __init__(self):
    self.labels = []
    self.policies = {}

  def addLabel(self, label):
    self.labels.append(label)

  # policy is a function from context to bool which returns true
  # if the label should be restricted
  def restrict(self, label, policy):
    pcFormula = JeevesGlobal.jeevesLib.pathenv.getPathFormula()
    self.policies[label] = fast.AST.Or(fast.AST.Not(pcFormula), policy)
