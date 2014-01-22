'''
Battleship game demo example.
'''
import JeevesLib
import Board
from Bomb import Bomb
from sourcetrans.macro_module import macros, jeeves

class Game:
  class NoSuchUserException(Exception):
    def __init__(self, u):
      self.u = u

  def __init__(self, boards):
    self.boards = boards
    self._moves = []

  def getBoard(self, user):
    try:
      return self.boards[user]
    except Exception:
      raise NoSuchUserException(user)

  @jeeves
  def allShipsPlaced(self):
    return JeevesLib.jall(map(lambda b: b.allPlaced(), self.boards.values()))

  @jeeves
  def gameOver(self):
    return not JeevesLib.jall(map(lambda b: not b.hasLost(), self.boards.values()))

  @jeeves
  def hasTurn(self, user):
    return (not self._moves) or (not self._moves[-1] == user)
  
  def bomb(self, ctxt, user, x, y):
    piece = self.getBoard(user).placeBomb(ctxt, x, y)
    self._moves.append(ctxt.user)
    return piece

'''
object BattleshipGame extends JeevesLib[GameContext] {
  val alice = User(0)
  val aliceBoard = Board(alice)
  val aliceBomb = Bomb(alice)

  val bob = User(1)
  val bobBoard = Board(bob)
  val bobBomb = Bomb(bob)

  val game = Game(Map(alice -> aliceBoard, bob -> bobBoard))
  val aliceCtxt = GameContext(alice, game)
  val bobCtxt =  GameContext(bob, game)

  // TODO: Make server socket so we can have two players playing at once.
  def main(args: Array[String]): Unit = {
    println("Welcome to this Battleship game.")

    // Alice's pieces.
    aliceBoard.placeShip(aliceCtxt, Carrier(alice), Point(0, 0), Point(0, 5))
    aliceBoard.placeShip(
      aliceCtxt, Battleship(alice), Point(1, 0), Point(1, 4))
    aliceBoard.placeShip(aliceCtxt, Cruiser(alice), Point(2, 0), Point(2, 3))
    aliceBoard.placeShip(
      aliceCtxt, Destroyer(alice), Point(3, 0), Point(3, 2))
    aliceBoard.placeShip(
      aliceCtxt, Destroyer(alice), Point(4, 0), Point(4, 2))
    aliceBoard.placeShip(
      aliceCtxt, Submarine(alice), Point(5, 0), Point(5, 1))
    aliceBoard.placeShip(
      aliceCtxt, Submarine(alice), Point(5, 1), Point(5, 2))
 
    // Bob's pieces.
    bobBoard.placeShip(
        bobCtxt, Carrier(bob), Point(0, 0), Point(0, 5))
    bobBoard.placeShip(
      bobCtxt, Battleship(bob), Point(1, 0), Point(1, 4))
    bobBoard.placeShip(bobCtxt, Cruiser(bob), Point(2, 0), Point(2, 3))
    bobBoard.placeShip(
      bobCtxt, Destroyer(bob), Point(3, 0), Point(3, 2))
    bobBoard.placeShip(
      bobCtxt, Destroyer(bob), Point(4, 0), Point(4, 2))
    bobBoard.placeShip(
      bobCtxt, Submarine(bob), Point(5, 0), Point(5, 1))
    bobBoard.placeShip(
      bobCtxt, Submarine(bob), Point(5, 1), Point(5, 2))

    game.bomb(bobCtxt, alice, 0, 0)
    game.bomb(aliceCtxt, bob, 0, 0)
    game.bomb(bobCtxt, alice, 1, 0)
    game.bomb(aliceCtxt, bob, 1, 0)
    game.bomb(bobCtxt, alice, 2, 0)
    game.bomb(aliceCtxt, bob, 2, 0)
    game.bomb(bobCtxt, alice, 3, 0)
    game.bomb(aliceCtxt, bob, 3, 0)
    game.bomb(bobCtxt, alice, 4, 0)
    game.bomb(aliceCtxt, bob, 4, 0)
    game.bomb(bobCtxt, alice, 5, 0)
    game.bomb(aliceCtxt, bob, 5, 0)
    game.bomb(bobCtxt, alice, 5, 1)
    //game.gameOver()

    /*
    // TODO: Listen until we get two players.
    while (!board0.hasLost() || !board1.hasLost()) {
      println("Player 0 board:")
      board0.printBoard()

      println("Player 1 board:")
      board1.printBoard()

      val input = readLine("prompt> ")
    }
    */
  }
'''
