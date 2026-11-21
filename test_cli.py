import contextlib
import io
import unittest
from unittest import mock

import ajedrez


def run(argv, inputs):
    """Run main() with scripted input; return the printed output and the final game."""
    games = []
    real_show = ajedrez.Game.show

    def show(self):
        games.append(self)
        real_show(self)

    out = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs) + [EOFError()]), \
            mock.patch.object(ajedrez.Game, "show", show), contextlib.redirect_stdout(out):
        ajedrez.main(argv)
    return out.getvalue(), games[-1]


class TestCLI(unittest.TestCase):
    def test_hint_suggests_a_legal_move_without_playing_it(self):
        out, game = run([], ["pista"])
        hint = out.split("Pista: ")[1].split()[0]
        self.assertTrue(game.white)
        self.assertTrue(ajedrez.Game().play(hint))

    def test_undo_two_players(self):
        out, game = run([], ["e2e4", "deshacer"])
        self.assertTrue(game.white)
        self.assertEqual(game.board, ajedrez.Game().board)
        out, _ = run([], ["deshacer"])
        self.assertIn("Nada que deshacer.", out)

    def test_undo_against_cpu_reverts_both_moves(self):
        _, game = run(["--cpu"], ["e2e4", "deshacer"])
        self.assertTrue(game.white)
        self.assertEqual(game.board, ajedrez.Game().board)

    def test_undo_when_cpu_plays_white_keeps_its_first_move(self):
        out, game = run(["--cpu", "blancas"], ["deshacer"])
        self.assertIn("Nada que deshacer.", out)
        self.assertFalse(game.white)

    def test_undo_restores_castling_and_en_passant(self):
        _, game = run([], ["e2e4", "a7a6", "e4e5", "d7d5", "e1e2", "deshacer"])
        self.assertEqual(game.en_passant, "d6")
        self.assertIn("h1", game.castling)
        self.assertTrue(game.white)

    def test_illegal_move_is_not_recorded(self):
        out, game = run([], ["e2e5", "deshacer"])
        self.assertIn("Movimiento ilegal", out)
        self.assertIn("Nada que deshacer.", out)


if __name__ == "__main__":
    unittest.main()
