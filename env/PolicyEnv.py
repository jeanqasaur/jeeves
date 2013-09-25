import JeevesGlobal
import fast.AST

class PolicyEnv:
  def __init__(self):
    self.labels = []
    self.policies = {}

  def addLabel(self, label):
    self.labels.append(label)

  # policy is a function from context to bool which returns true
  # if the label is allowed to be HIGH
  def restrict(self, label, policy):
    pcFormula = JeevesGlobal.jeevesLib.pathenv.getPathFormula()
    self.policies[label] = (lambda ctxt :
      fast.AST.Implies(
        fast.AST.fexpr_cast(pcFormula),
        policy(ctxt),
      )
    )

  # Takes a context and an expression
  def concretizeExp(ctxt, f):
    dependencies = defaultdict(set)
    constraints = []
    # First, find all all the dependencies between labels
    # and add Not(predicate) ==> label == LOW conditions
    for (label, policy) in self.policies.iteritems():
      predicate = policy(f) #predicate should be True if label can be HIGH
      predicate_vars = predicate.vars()
      dependencies |= predicate_vars
      constraints.append(fast.AST.Implies(label, predicate))

    # If a depends on b, then we want (b == Low ==> a == Low)
    for (label, label_deps) in dependencies.iteritems():
      for label_dep in label_deps:
        constraints.append(fast.AST.Implies(label, label_dep))

    #TODO pass constraints to solver
    #TODO test this
