import macropy.activate
import JeevesLib
from smt.Z3 import *
import unittest
from Battleship import Game
from Board import Board
from Bomb import Bomb
from GameContext import GameContext
from GamePiece import Carrier, Battleship, Cruiser, Destroyer, Submarine, NoShip
from Point import Point
from User import User

class TestBattleship(unittest.TestCase):
  def setUp(self):
    JeevesLib.init()

    self.alice = User(0)
    self.aliceBoard = Board(self.alice)
    self.aliceBomb = Bomb(self.alice)

    self.bob = User(1)
    self.bobBoard = Board(self.bob)
    self.bobBomb = Bomb(self.bob)

    self.game = Game({self.alice: self.aliceBoard, self.bob: self.bobBoard})
    self.aliceCtxt = GameContext(self.alice, self.game)
    self.bobCtxt =  GameContext(self.bob, self.game)

  def test_can_only_put_pieces_on_board(self):
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Carrier(self.alice), Point(0, 0), Point(0, 5)))
    
    # Cannot place the same piece again.
    self.assertFalse(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Carrier(self.alice), Point(0,0), Point(0, 5)))

    # Cannot place another piece at the same location.
    self.assertFalse(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Battleship(self.alice), Point(0, 0), Point(0, 4)))
    
    # self.assertFalse(self.aliceBoard.allPlaced())

  '''
  test ("Cannot place bombs until all pieces have been placed") {
    expectResult(false) {
      aliceBoard.getSquare(0, 0).bomb(bobCtxt, bobBomb)
    }
  }

  test ("Bob cannot put a ship on Alice's board") {
    expectResult(false) {
      aliceBoard.placeShip(bobCtxt, Battleship(bob), Point(1, 0), Point(1, 4))
    }
  }

  test ("Putting the rest of of Alice's pieces") {
    expectResult(true) {
      aliceBoard.placeShip(
        aliceCtxt, Battleship(alice), Point(1, 0), Point(1, 4))
    }
    expectResult(true) {
      aliceBoard.placeShip(aliceCtxt, Cruiser(alice), Point(2, 0), Point(2, 3))
    }
    expectResult(true) {
      aliceBoard.placeShip(
        aliceCtxt, Destroyer(alice), Point(3, 0), Point(3, 2))
    }
    expectResult(true) {
      aliceBoard.placeShip(
        aliceCtxt, Destroyer(alice), Point(4, 0), Point(4, 2))
    }
    expectResult(true) {
      aliceBoard.placeShip(
        aliceCtxt, Submarine(alice), Point(5, 0), Point(5, 1))
    }
    expectResult(true) {
      aliceBoard.placeShip(
        aliceCtxt, Submarine(alice), Point(5, 1), Point(5, 2))
    }
  }

  test ("Cannot put pieces after they have already been placed") {
    expectResult(false) {
      aliceBoard.placeShip(
        aliceCtxt, Submarine(alice), Point(6,0), Point(6, 1))
    }
  }

  test ("Cannot put bombs until all ships have been placed") {
    expectResult(false) {
      aliceBoard.getSquare(0, 0).bomb(bobCtxt, bobBomb)
    }
  }

  test ("Putting all of Bob's pieces") {
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Carrier(bob), Point(0, 0), Point(0, 5))
    }
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Battleship(bob), Point(1, 0), Point(1, 4))
    }
    expectResult(true) {
      bobBoard.placeShip(bobCtxt, Cruiser(bob), Point(2, 0), Point(2, 3))
    }
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Destroyer(bob), Point(3, 0), Point(3, 2))
    }
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Destroyer(bob), Point(4, 0), Point(4, 2))
    }
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Submarine(bob), Point(5, 0), Point(5, 1))
    }
    expectResult(true) {
      bobBoard.placeShip(
        bobCtxt, Submarine(bob), Point(5, 1), Point(5, 2))
    }
  }

  test ("Can bomb a piece with no ship") {
    expectResult(NoShip) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 9, 9))
    }
  }

  test ("Can bomb a piece with a ship") {
    expectResult(Carrier(alice)) {
      concretize(aliceCtxt, game.bomb(bobCtxt, alice, 0, 0))
    }
  }

  test ("Cannot put two bombs in a row") {
    expectResult(NoShip) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 0, 0))
    }
  }

  test ("Can see ship if bombed") {
    // debugPrint(bobCtxt, aliceBoard.getSquare(0, 0).getShip())(BattleshipGame)
    expectResult(Carrier(alice)) {
      concretize(bobCtxt, aliceBoard.getSquare(0, 0).getShip())
    }
    expectResult(Carrier(alice)) {
      concretize(bobCtxt, aliceBoard.getSquare(0, 3).getShip())
    }            
  }

  test ("Cannot see ship if not bombed") {
    expectResult(NoShip) {
      concretize(aliceCtxt, bobBoard.getSquare(0, 0).getShip())
    }
  }

  test ("Playing the rest of the game..." ) {
    expectResult(Carrier(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 0, 0))
    }
    expectResult(Battleship(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 1, 0))
    }
    expectResult(Battleship(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 1, 0))
    }
    expectResult(Cruiser(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 2, 0))
    }
    expectResult(Cruiser(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 2, 0))
    }
    expectResult(Destroyer(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 3, 0))
    }
    expectResult(Destroyer(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 3, 0))
    }
    expectResult(Destroyer(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 4, 0))
    }
    expectResult(Destroyer(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 4, 0))
    }
    expectResult(Submarine(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 5, 0))
    }
    expectResult(Submarine(bob)) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 5, 0))
    }
    expectResult(Submarine(alice)) {
      concretize(bobCtxt, game.bomb(bobCtxt, alice, 5, 1))
    }
    expectResult(true) {
      game.gameOver()
    }
  }

  test ("Cannot place ships once somebody has won") {
    expectResult(NoShip) {
      concretize(aliceCtxt, game.bomb(aliceCtxt, bob, 5, 1))
    }
  }

  test ("Can see all ships once done") {
    expectResult(Submarine(bob)) {
      concretize(aliceCtxt, bobBoard.getSquare(5, 1).getShip())
    }
  }
  '''

if __name__ == '__main__':
    unittest.main()
