'''
Defines a battleship game board.
'''
import JeevesLib
from Bomb import Bomb
from GamePiece import Carrier, Battleship, Cruiser, Destroyer, Submarine, NoShip
from sourcetrans.macro_module import macros, jeeves
from Square import Square

class Board:
  class OutOfBoundsException(Exception):
    pass

  def __init__(self, owner):
    self.owner = owner  
    self.boardSize = 10
    
    # Initialize the board.
    self.board = []
    for i in range(0, self.boardSize):
      curCol = []
      for j in range(0, self.boardSize):      
        curCol.append(Square(self.owner))
      self.board.append(curCol)    

    self.pieces = [ Carrier(owner), Battleship(owner), Cruiser(owner)
                  , Destroyer(owner), Destroyer(owner)
                  , Submarine(owner), Submarine(owner) ]

  def getSquare(self, x, y):
    return self.board[x][y]

  # Places a ship on the board. Looks in the list of current pieces to mark
  # it as placed. Updates the ship and the board.
  @jeeves
  def placeShip(self, ctxt, ship, start, end):
    for cur in self.pieces:
      if cur == ship and not cur.isPlaced():
        # Update the relevant board pieces.
        pts = cur.getPiecePoints(start, end)
        if not (pts == None):
          for pt in pts:
            shipUpdated = self.board[pt.x][pt.y].updateShip(ctxt, cur)
            squareUpdated = cur.addSquare(self.board[pt.x][pt.y])
            if not (shipUpdated and squareUpdated):
              return False
          return cur.placePiece(ctxt)
        # If the points didn't fit, then we can't place the ship.
        else:        
            print "Piece didn't fit: "
            print ship
            print "\n"
            return False
    print "Don't have piece to play: "
    print ship
    print "\n"
    return False

  # Places a bomb. Updates the specific square on the board. If there is a
  # ship at this point, this function also updates the ship with the fact that
  # it has been bombed.
  # NOTE: This seems to be a problematic function causing some tests to fail...
  @jeeves
  def placeBomb(self, ctxt, x, y):
    if x < self.boardSize and y < self.boardSize:
      boardShip = self.board[x][y].getShip()
      bomb = Bomb(ctxt.user)
      bombedPoint = self.board[x][y].bomb(ctxt, bomb)
      # TODO: The problem here is that the call to all is not on a list, but
      # an FObject or potentially, Unassigned.
      succeeded = (bombedPoint if boardShip == NoShip()
                    else all(map(lambda s: s.bomb(ctxt, bomb) and
                              s.bombPiece(ctxt), boardShip.getSquares())))
      return boardShip if succeeded else NoShip()
    else:
      print "Bomb location outside of board: (" + x + ", " + y + ")" + "\n"
      raise OutOfBoundsException

  # Determines if all of a player's pieces have been placed. This variable
  # should always be concrete.
  def allPlaced(self):
    return all(map(lambda p: p.isPlaced(), self.pieces))
  # Determines if all pieces on the board have been bombed. This variable
  # should always be concrete.
  def hasLost(self):
    return all(map(lambda p: p.isBombed(), self.pieces))

  def printBoard(self, ctxt):
    for j in range(0, 10):
      for i in range(0, 10):
        curSquare = self.board[i][j]
        if JeevesLib.concretize(ctxt, curSquare.hasBomb()):
          print("X")
        elif concretize(ctxt, curSquare.hasShip()):
          print("S")
        else:
          print("W")
      print("\n")

  def printUnplacedPieces(self):
    print "Remaining unplaced pieces:\n"
    for p in self.pieces:
      if not p.isPlaced():
        print p
        print "\n"

  def printRemainingPieces(self):
    print "Remaining pieces:\n"
    for p in self.pieces:
      if not p.isBombed():
        print p
        print "\n"
