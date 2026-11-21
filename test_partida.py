import unittest

from ajedrez import Game
from partida import Partida


class TestPartida(unittest.TestCase):
    def test_play_and_undo_two_players(self):
        p = Partida()
        self.assertFalse(p.undo())
        self.assertFalse(p.play("e2e5"))
        self.assertTrue(p.play("e2e4"))
        self.assertEqual(p.player, "Negras")
        self.assertTrue(p.undo())
        self.assertEqual(p.game.board, Game().board)

    def test_cpu_turn_move_and_undo(self):
        p = Partida("negras")
        self.assertFalse(p.cpu_turn())
        p.play("e2e4")
        self.assertTrue(p.cpu_turn())
        move = p.cpu_move()
        self.assertEqual(len(p.history), 2)
        self.assertNotIn(move[:2], p.game.board)
        self.assertTrue(p.undo())
        self.assertEqual(p.game.board, Game().board)
        self.assertTrue(p.game.white)

    def test_hint_does_not_change_state(self):
        p = Partida()
        hint = p.hint()
        self.assertTrue(Game().play(hint))
        self.assertEqual(p.history, [])
        self.assertTrue(p.game.white)

    def test_status_and_no_cpu_turn_after_game_over(self):
        # White (the machine) is checkmated: it must not try to move.
        p = Partida("blancas")
        for move in ["f2f3", "e7e5", "g2g4", "d8h4"]:
            p.game.play(move)
        self.assertEqual(p.status(), "jaque_mate")
        self.assertFalse(p.cpu_turn())

    def test_invalid_cpu_color(self):
        with self.assertRaises(ValueError):
            Partida("rojas")


if __name__ == "__main__":
    unittest.main()
