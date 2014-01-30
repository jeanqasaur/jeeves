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

    self.alice = User(0, "Alice")
    self.aliceBoard = Board(self.alice)
    self.aliceBomb = Bomb(self.alice)

    self.bob = User(1, "Bob")
    self.bobBoard = Board(self.bob)
    self.bobBomb = Bomb(self.bob)

    self.game = Game({self.alice: self.aliceBoard, self.bob: self.bobBoard})
    self.aliceCtxt = GameContext(self.alice, self.game)
    self.bobCtxt =  GameContext(self.bob, self.game)

  def can_only_place_piece_on_own_board(self):
    # Bob cannot put pieces on Alice's board.
    self.assertFalse(
      self.aliceBoard.placeShip(
        self.bobCtxt, Battleship(self.bob), Point(1, 0), Point(1, 4)))

  def test_placing_pieces(self):
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
    
    self.assertFalse(
      JeevesLib.concretize(self.aliceCtxt, self.aliceBoard.allPlaced()))
    self.assertFalse(
      JeevesLib.concretize(self.bobCtxt, self.aliceBoard.allPlaced()))

    # Cannot bomb until all pieces placed.
    self.assertFalse(
      self.aliceBoard.getSquare(0, 0).bomb(self.bobCtxt, self.bobBomb))

    # Putting the rest of Alice's pieces...
    self.assertTrue(    
      self.aliceBoard.placeShip(
        self.aliceCtxt, Battleship(self.alice), Point(1, 0), Point(1, 4)))
    
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Cruiser(self.alice), Point(2, 0), Point(2, 3)))
    
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Destroyer(self.alice), Point(3, 0), Point(3, 2)))
    
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Destroyer(self.alice), Point(4, 0), Point(4, 2)))
    
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Submarine(self.alice), Point(5, 0), Point(5, 1)))
    
    self.assertTrue(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Submarine(self.alice), Point(5, 1), Point(5, 2)))

    # Cannot put more pieces than are available.
    self.assertFalse(
      self.aliceBoard.placeShip(
        self.aliceCtxt, Submarine(self.alice), Point(6,0), Point(6, 1)))

    #  Putting Bob's pieces... 
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Carrier(self.bob), Point(0, 0), Point(0, 5)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Battleship(self.bob), Point(1, 0), Point(1, 4)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Cruiser(self.bob), Point(2, 0), Point(2, 3)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Destroyer(self.bob), Point(3, 0), Point(3, 2)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Destroyer(self.bob), Point(4, 0), Point(4, 2)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Submarine(self.bob), Point(5, 0), Point(5, 1)))
    self.assertTrue(
      self.bobBoard.placeShip(
        self.bobCtxt, Submarine(self.bob), Point(5, 1), Point(5, 2)))

    # Can bomb a piece with no ship.
    self.assertEqual(NoShip()
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 9, 9)))

    # Can bomb a piece with some ship.
    self.assertEqual(Carrier(self.alice)
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.bobCtxt, self.alice, 0, 0)))

    self.assertEqual(NoShip()
      , JeevesLib.concretize(
          self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 0, 0)))

    self.assertEqual(Carrier(self.alice)
      , JeevesLib.concretize(
          self.bobCtxt, self.aliceBoard.getSquare(0, 0).getShip()))
    self.assertEqual(Carrier(self.alice)
      , JeevesLib.concretize(
          self.bobCtxt, self.aliceBoard.getSquare(0, 3).getShip()))

    self.assertEqual(NoShip()
      , JeevesLib.concretize(
          self.aliceCtxt, self.bobBoard.getSquare(0, 0).getShip()))
    
    self.assertEqual(Carrier(self.bob)
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 0, 0)))
    self.assertEqual(Battleship(self.alice)
      , JeevesLib.concretize(
          self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 1, 0)))
    self.assertEqual(Battleship(self.bob)
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 1, 0)))
    self.assertEqual(Cruiser(self.alice)
      , JeevesLib.concretize(
          self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 2, 0)))
    self.assertEqual(Cruiser(self.bob)
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 2, 0)))
    self.assertEqual(Destroyer(self.alice)
      , JeevesLib.concretize(
          self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 3, 0)))
    self.assertEqual(Destroyer(self.bob)
      , JeevesLib.concretize(
          self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 3, 0)))
    self.assertEqual(Destroyer(self.alice)
      , JeevesLib.concretize(
        self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 4, 0)))
    self.assertEqual(Destroyer(self.bob)
      , JeevesLib.concretize(
        self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 4, 0)))
    self.assertEqual(Submarine(self.alice)
      , JeevesLib.concretize(
        self.bobCtxt, self.game.bomb(self.bobCtxt, self.alice, 5, 0)))
    self.assertEqual(Submarine(self.bob)
      , JeevesLib.concretize(
        self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 5, 0)))
    self.assertTrue(self.game.gameOver())

    self.assertEqual(NoShip()
      , JeevesLib.concretize(
        self.aliceCtxt, self.game.bomb(self.aliceCtxt, self.bob, 5, 1)))
    
    self.assertEqual(Submarine(self.bob)
      , JeevesLib.concretize(
        self.aliceCtxt, self.bobBoard.getSquare(5, 1).getShip()))

if __name__ == '__main__':
    unittest.main()
