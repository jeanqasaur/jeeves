from Chemotaxis import Protein, BlueProtein, Chemotaxis, GreenProtein, PProtein, RedProtein, YellowProtein, EdgeType

class RSphaeroides(Chemotaxis):
  # Define the structure of the cell in terms of connections.
  # TODO: How do we specify initial values for proteins where there are more
  # than one of the same?
  def __init__(self, values={}):
    Chemotaxis.__init__(self)

    self.proteinMCP = GreenProtein("MCP")
    self._ligandEdges.append(self.proteinMCP)
    self.proteinW2 = GreenProtein("W2")
    self.proteinW3 = GreenProtein("W3")
    self.proteinA2_0 = GreenProtein("A2")
    self.proteinA2_1 = GreenProtein("A2")
    self.proteinR2 = RedProtein("R2")
    self.proteinR2.addEdge(self.proteinMCP, EdgeType.Methylation)
    self.proteinP_0 = Protein("P")
    self.proteinA2_1.addEdge(self.proteinP_0, EdgeType.PhosphoTransfer)

    self.proteinTlp = GreenProtein("Tlp")
    self._ligandEdges.append(self.proteinMCP)
    self.proteinW4 = GreenProtein("R4")
    self.proteinA4 = GreenProtein("A4")
    self.proteinA3 = GreenProtein("A3")
    self.proteinR3 = RedProtein("R3")
    self.proteinR3.addEdge(self.proteinTlp, EdgeType.Methylation)
    self.proteinP_1 = Protein("P")
    self.proteinA4.addEdge(self.proteinP_1, EdgeType.PhosphoTransfer)
  
    self.proteinB1_0 = YellowProtein("B1")
    self.proteinB1_1 = YellowProtein("B1")
    self.proteinB1_0.addEdge(self.proteinB1_1, EdgeType.FlagellumControl)
    self.proteinB1_1.addEdge(self.proteinB1_0, EdgeType.FlagellumControl)
    self.proteinP_2 = Protein("P") 
    # TODO: How to add a phosphotransfer with an edge?

    self.proteinY6_1 = BlueProtein("Y6")
    self.proteinY6_1.addEdge(self._flagellumOut, EdgeType.FlagellumControl)
    
    self.proteins = [ self.proteinMCP, self.proteinW2, self.proteinW3
                    , self.proteinA2_0, self.proteinA2_1, self.proteinR2
                    , self.proteinP_0, self.proteinTlp, self.proteinA4
                    , self.proteinA3, self.proteinR3, self.proteinP_1
                    , self.proteinB1_0, self.proteinB1_1, self.proteinP_2 ]
