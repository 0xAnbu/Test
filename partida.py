"""Historial de turnos compartido por las dos interfaces."""

from copy import deepcopy

from ajedrez import Game


class Partida:
    def __init__(self, cpu=None):
        self.game = Game()
        self.cpu = cpu
        self.history = []

    def play(self, move):
        human_turn = self.cpu is None or self.game.white != self.cpu
        before = deepcopy(self.game) if human_turn else None
        if not self.game.play(move):
            return False
        if before is not None:
            self.history.append(before)
        return True

    def can_undo(self):
        return bool(self.history)

    def undo(self):
        if not self.can_undo():
            return False
        self.game = self.history.pop()
        return True
