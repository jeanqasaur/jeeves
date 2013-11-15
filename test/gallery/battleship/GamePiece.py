from abc import ABCMeta, abstractmethod
from sourcetrans.macro_module import macros, jeeves
import JeevesLib
from util.Singleton import Singleton

@jeeves
class GamePiece:
  __metaclass__ = ABCMeta

  def __init__(self, owner):
    self.owner = owner  
    self.placedRef = ProtectedRef(False
      , lambda hasShip: lambda ic: (not hasShip) and self.isOwner(ic)
      , None)
    # TODO: See if we can do away with this...
    self.placed = False

    self.bombedRef = ProtectedRef(False
      , lambda hasBomb: lambda ic: not hasBomb
      , None)
    # TODO: See if we can do away with this...
    self.bombed = False

    self.squares = []

  def isOwner(self, ctxt):
    return ctxt.user == self.owner

  def placePiece(self, ctxt):
    if (self.placedRef.update(ctxt, ctxt, true) == UpdateResult.Success):
      self.placed = True
      return True
    else:
      return False
  def isPlaced(self):
    return self.placed
  
  def bombPiece(self, ctxt):
    if (self.bombedRef.update(ctxt, ctxt, true) == UpdateResult.Success):
      self.bombed = True;
      return True
    else:
      return False  
  def isBombed(self):
    return self.bombed

  def getPiecePoints(self, start, end):
    if start.inLine(end) and start.distance(end) == size:
      # If we are on the same horizontal line...
      if start.x == end.x:
        yPts = range(start.y
                      , end.y) if start.y < end.y else range(end.y, start.y)
        return map(lambda yPt: Point(start.x, yPt), yPts)
      else:
        xPts = range(start.x
                      , end.x) if start.x < end.x else range(end.x, start.x)
        return map(lambda xPt: Point(xPt, start.y), xPts)
    else:
      return None
  
  # TODO: Return whether the update succeeded...
  def addSquare(self, s):
    self.squares.append(s)
    return True
  def getSquares(self):
    return self.squares

class Carrier(GamePiece):
  def __init__(self, owner):
    self.size = 5
    GamePiece.__init__(self, owner)
class Battleship(GamePiece):
  def __init__(self, owner):
    self.size = 4
    GamePiece.__init__(self, owner)
class Cruiser(GamePiece):
  def __init__(self, owner):
    self.size = 3
    GamePiece.__init__(self, owner)
class Destroyer(GamePiece):
  def __init__(self, owner):
    self.size = 2
    GamePiece.__init__(self, owner)
class Submarine(GamePiece):
  def __init__(self, owner):
    self.size = 1
    GamePiece.__init__(self, owner)
class NoShip(GamePiece, Singleton):
  def __init__(self):
    self.size = 0
    self.owner = None
