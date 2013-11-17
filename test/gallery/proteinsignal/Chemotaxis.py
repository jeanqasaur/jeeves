'''
We try to model chemotaxis as an information flow system, where receptor
sensitivities correspond to flow permissions.
'''
from macropy.case_classes import macros, enum
import JeevesLib
from fast.ProtectedRef import ProtectedRef
from sourcetrans.macro_module import macros, jeeves

class Impossible(Exception):
  def __init__(self, msg):
    self.msg = msg

# TODO: Add an adjacency edge?
@enum
class EdgeType:
  ReceptorActivation, PhosphoTransfer, Methylation, FlagellumControl

class Edge:
  def __init__(self, v, edgeType):
    self.v = v
    self.edgeType = edgeType

@jeeves
class Protein:
  # TODO: Figure out what kinds of policies should go here...
  def __init__(self, name, initValue=0):
    self.name = name
    self._vRef = ProtectedRef(initValue
      # We also support policies where the write checks get concretized right
      # away in the context of the user.
      , None
      # Flow is only permitted if there is an edge.
      # The policy takes the current value (v), the input channel (ic), and
      # the output channel.
      , lambda v: lambda ic: lambda oc:
          JeevesLib.jhasElt(self.edges, lambda edge: edge.v == oc))
    self._edges = []
  def addEdge(self, node, edgeType):
    self._edges.append(Edge(node, edgeType))
  def updateValue(self, ictxt, f):
    self._vRef.update(ictxt, ictxt, f(self._vRef.v))

# TODO: Do these different color proteins have different properties?
class BlueProtein(Protein):
  pass
class GreenProtein(Protein):
  pass
class PProtein(Protein):
  pass
class RedProtein(Protein):
  pass
class YellowProtein(Protein):
  pass

'''
This class defines chemotaxis actions for a set of proteins (in a bacteria
cell?
'''
class Chemotaxis:
  def __init__(self):
    self.proteins = []
    self._ligandEdges = []
    self._flagellumOut = Protein("FOut")

  # TODO: Change the update functions to update to what they should actually do.
  def runStep(self):
    for protein in self.proteins:
      # TODO: Add a case for adjacency?
      for edge in self.edges:
        if edge.edgeType == EdgeType.ReceptorActivation:
          edge.v.updateValue(lambda v: v)
        elif edge.edgeType == Edgetype.PhosphoTransfer:
          edge.v.updateValue(lambda v: v)
        elif edge.edgeType == EdgeType.Methylation:
          edge.v.updateValue(lambda v: v)
        elif edge.edgeType ==FlagellumControl:
          edge.v.updateValue(lambda v: v)
        else:
          raise Impossible("Edge should be one of the above types.")
