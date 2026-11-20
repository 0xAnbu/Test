import time
import unittest

from ajedrez import Game
from ia import best_move, legal_moves


def position(pieces, white=True, castling=()):
    return Game(board=dict(pieces), white=white, castling=set(castling))


class TestIA(unittest.TestCase):
    def test_legal_moves_initial_and_special(self):
        self.assertEqual(len(legal_moves(Game())), 20)
        castle = position({"e1": "K", "h1": "R", "e8": "k"}, castling={"h1"})
        self.assertIn("e1g1", legal_moves(castle))
        promo = position({"a7": "P", "e1": "K", "h8": "k"})
        self.assertTrue({"a7a8q", "a7a8r", "a7a8b", "a7a8n"} <= set(legal_moves(promo)))

    def test_finds_mate_in_one(self):
        game = position({"g1": "K", "a1": "R", "g8": "k", "f7": "p", "g7": "p", "h7": "p"})
        self.assertEqual(best_move(game), "a1a8")
        self.assertEqual(best_move(game, depth=1), "a1a8")

    def test_rejects_invalid_depth(self):
        for depth in (0, -1, 1.5):
            with self.subTest(depth=depth), self.assertRaises(ValueError):
                best_move(Game(), depth=depth)

    def test_finds_mate_in_one_for_black(self):
        game = Game()
        for move in ["f2f3", "e7e5", "g2g4"]:
            game.play(move)
        self.assertEqual(best_move(game), "d8h4")

    def test_captures_hanging_queen(self):
        game = position({"e1": "K", "d1": "R", "d5": "q", "a8": "k"})
        self.assertEqual(best_move(game), "d1d5")

    def test_does_not_hang_its_queen(self):
        # Moving the queen to e5/d6 lets a pawn take it; the engine must avoid that.
        game = position({"e1": "K", "d4": "Q", "a8": "k", "f6": "p", "c7": "p"})
        move = best_move(game)
        self.assertNotIn(move, {"d4e5", "d4d6", "d4b6"})
        self.assertTrue(game.play(move))

    def test_no_moves_returns_none(self):
        stalemate = position({"a8": "k", "b6": "Q", "c7": "K"}, white=False)
        self.assertIsNone(best_move(stalemate))

    def test_is_deterministic_and_fast_enough(self):
        start = time.perf_counter()
        first = best_move(Game())
        self.assertLess(time.perf_counter() - start, 10)
        self.assertEqual(first, best_move(Game()))
        self.assertIn(first, legal_moves(Game()))


if __name__ == "__main__":
    unittest.main()
