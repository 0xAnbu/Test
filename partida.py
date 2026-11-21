"""Estado de una partida con historial: jugar, deshacer, pista y turno de la máquina.

Lo comparten la terminal (ajedrez.py) y la interfaz gráfica.
"""

import copy

from ajedrez import Game


class Partida:
    def __init__(self, cpu=None):
        """cpu: None (dos jugadores), "blancas" o "negras" (color de la máquina)."""
        if cpu not in (None, "blancas", "negras"):
            raise ValueError(f"cpu inválido: {cpu!r}")
        self.cpu = cpu
        self.game = Game()
        self.history = []

    @property
    def player(self):
        return "Blancas" if self.game.white else "Negras"

    def cpu_turn(self):
        return self.cpu is not None and self.player.lower() == self.cpu and self.status() == "jugando"

    def status(self):
        """'jugando', 'jaque_mate' o 'ahogado'."""
        if self.game.has_legal_move():
            return "jugando"
        return "jaque_mate" if self.game.in_check() else "ahogado"

    def play(self, move):
        """Juega una jugada UCI; False si es ilegal (no se registra)."""
        before = copy.deepcopy(self.game)
        if not self.game.play(move):
            return False
        self.history.append(before)
        return True

    def cpu_move(self, depth=3):
        """Hace jugar a la máquina y devuelve su jugada."""
        from ia import best_move

        move = best_move(self.game, depth)
        if move is None or not self.play(move):
            raise RuntimeError("La máquina no devolvió una jugada legal.")
        return move

    def hint(self, depth=3):
        """Jugada sugerida, sin jugarla; None si no hay jugadas."""
        from ia import best_move

        return best_move(self.game, depth)

    def _undo_index(self):
        for index in range(len(self.history) - 1, -1, -1):
            state = self.history[index]
            color = "blancas" if state.white else "negras"
            if self.cpu != color:
                return index
        return None

    def can_undo(self):
        return self._undo_index() is not None

    def undo(self):
        """Vuelve al estado anterior a la última jugada humana."""
        index = self._undo_index()
        if index is None:
            return False
        self.game = self.history[index]
        del self.history[index:]
        return True
