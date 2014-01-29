import JeevesLib
from fast.ProtectedRef import ProtectedRef, UpdateResult
from GamePiece import NoShip
from sourcetrans.macro_module import macros, jeeves

@jeeves
class Square:
  @jeeves
  def __init__(self, owner):
    self.owner = owner
    self.shipRef = ProtectedRef(NoShip()
      # Policy for updating: must be owner and there can't be a ship there
      # already.
      , lambda ship: lambda ic: ship == NoShip()
      , lambda ship: lambda ic: lambda _oc: self.isOwner(ic))
    self.hasBombRef = ProtectedRef(None
      , lambda _bomb: lambda ic: self.hasTurn(ic)
      , lambda _bomb: lambda ic: lambda _oc:
          self.hasTurn(ic) and self.allShipsPlaced(ic) and
            (not self.gameOver(ic)))

  def isOwner(self, ctxt):
    return ctxt.user == self.owner
  # TODO: Make sure function applications get applied correctly here.
  # Do we need another @jeeves annotation?
  def hasTurn(self, ctxt):
    return ctxt.game.hasTurn(ctxt.user)
  def allShipsPlaced(self, ctxt):
    return ctxt.game.allShipsPlaced()
  def gameOver(self, ctxt):
    return ctxt.game.gameOver()
  @jeeves
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

  @jeeves
  def bomb(self, ctxt, bomb):
    r = self.hasBombRef.update(ctxt, ctxt, bomb) == UpdateResult.Success
    print 'hasTurn is', self.hasTurn(ctxt)
    print 'allShipsPlaced is', self.allShipsPlaced(ctxt)
    print 'gameOver is', self.gameOver(ctxt)
    print 'update bomb is', r
    return r
  
  def hasBomb(self):
    return not (self.hasBombRef.v == None)
