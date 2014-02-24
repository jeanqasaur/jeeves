import JeevesLib
from fast.ProtectedRef import ProtectedRef, UpdateResult
from GamePiece import NoShip
from sourcetrans.macro_module import macros, jeeves

@jeeves
class Square:
  def __init__(self, owner):
    self.owner = owner
    self.shipRef = ProtectedRef(NoShip()
      # Policy for updating: must be owner and there can't be a ship there
      # already.
      , lambda ship: lambda ic: ship == NoShip()
      , lambda ship: lambda ic: lambda _oc: self.isOwner(ic))
    self.hasBombRef = ProtectedRef(None
      , lambda _bomb: lambda ic:
          self.hasTurn(ic) and self.allShipsPlaced(ic) and
            not self.gameOver(ic)
      , None)

  def isOwner(self, ctxt):
    return ctxt.user == self.owner
  def hasTurn(self, ctxt):
    return ctxt.game.hasTurn(ctxt.user)
  def allShipsPlaced(self, ctxt):
    return ctxt.game.allShipsPlaced()
  def gameOver(self, ctxt):
    return ctxt.game.gameOver()
  def mkShipSecret(self, ship):
    a = JeevesLib.mkLabel("ship")
    JeevesLib.restrict(a
      , lambda ctxt:
          self.hasBomb() or self.isOwner(ctxt) or self.gameOver(ctxt));
    return JeevesLib.mkSensitive(a, ship, NoShip())

  # Returns whether updating a square's ship reference succeeded.
  def updateShip(self, ctxt, ship):
    return self.shipRef.update(ctxt, ctxt, self.mkShipSecret(ship)) == UpdateResult.Success
  def hasShip(self):
    return not self.shipRef.v == NoShip()
  def getShip(self):
    return self.shipRef.v

  def bomb(self, ctxt, bomb):
    r = self.hasBombRef.update(ctxt, ctxt, bomb)
    print 'moooooooooo', r
    return r == UpdateResult.Success
  
  def hasBomb(self):
    return not (self.hasBombRef.v == None)
