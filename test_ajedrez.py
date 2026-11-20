import unittest

from ajedrez import Game


def position(pieces, white=True, castling=()):
    return Game(board=dict(pieces), white=white, castling=set(castling))


def play_all(game, moves):
    for move in moves:
        assert game.play(move), move


class TestAjedrez(unittest.TestCase):
    def test_initial_moves_and_turn(self):
        game = Game()
        self.assertTrue(game.has_legal_move())
        self.assertFalse(game.in_check())
        self.assertTrue(game.play("e2e4"))
        self.assertFalse(game.white)
        self.assertEqual(game.board["e4"], "P")
        self.assertNotIn("e2", game.board)

    def test_illegal_and_malformed_moves_are_rejected(self):
        game = Game()
        for bad in ["e2e5", "e7e5", "z9z9", "e2", "", "e1e2", "g1g3", "e2e4k"]:
            self.assertFalse(game.play(bad), bad)
        self.assertTrue(game.white)

    def test_fools_mate(self):
        game = Game()
        play_all(game, ["f2f3", "e7e5", "g2g4", "d8h4"])
        self.assertTrue(game.in_check())
        self.assertFalse(game.has_legal_move())

    def test_stalemate(self):
        game = position({"a8": "k", "b6": "Q", "c7": "K"}, white=False)
        self.assertFalse(game.in_check())
        self.assertFalse(game.has_legal_move())

    def test_pinned_piece_cannot_leave_line(self):
        game = position({"e1": "K", "e2": "R", "e8": "r", "a8": "k"})
        self.assertFalse(game.play("e2d2"))
        self.assertTrue(game.play("e2e8"))

    def test_promotion_default_and_suffix(self):
        game = position({"a7": "P", "e1": "K", "h8": "k"})
        self.assertTrue(game.play("a7a8"))
        self.assertEqual(game.board["a8"], "Q")
        game = position({"a7": "P", "e1": "K", "h8": "k"})
        self.assertTrue(game.play("a7a8n"))
        self.assertEqual(game.board["a8"], "N")
        self.assertFalse(position({"e1": "K", "h8": "k", "a1": "R"}).play("a1a2q"))

    def test_en_passant_only_right_after_double_step(self):
        game = Game()
        play_all(game, ["e2e4", "a7a6", "e4e5", "d7d5"])
        self.assertTrue(game.play("e5d6"))
        self.assertNotIn("d5", game.board)
        game = Game()
        play_all(game, ["e2e4", "a7a6", "e4e5", "d7d5", "a2a3", "a6a5"])
        self.assertFalse(game.play("e5d6"))

    def test_castling(self):
        game = position({"e1": "K", "h1": "R", "a1": "R", "e8": "k"}, castling={"a1", "h1"})
        self.assertTrue(game.play("e1g1"))
        self.assertEqual((game.board["g1"], game.board["f1"]), ("K", "R"))
        game = position({"e1": "K", "a1": "R", "e8": "k"}, castling={"a1"})
        self.assertTrue(game.play("e1c1"))
        self.assertEqual((game.board["c1"], game.board["d1"]), ("K", "R"))

    def test_castling_blocked_by_check_attack_or_lost_rights(self):
        # In check.
        self.assertFalse(position({"e1": "K", "h1": "R", "e8": "r", "a8": "k"}, castling={"h1"}).play("e1g1"))
        # Passing through an attacked square.
        self.assertFalse(position({"e1": "K", "h1": "R", "f8": "r", "a8": "k"}, castling={"h1"}).play("e1g1"))
        # Piece in between.
        self.assertFalse(position({"e1": "K", "h1": "R", "g1": "N", "a8": "k"}, castling={"h1"}).play("e1g1"))
        # Rights lost after the king moves and returns.
        game = position({"e1": "K", "h1": "R", "a8": "k"}, castling={"h1"})
        play_all(game, ["e1e2", "a8b8", "e2e1", "b8a8"])
        self.assertFalse(game.play("e1g1"))


if __name__ == "__main__":
    unittest.main()
