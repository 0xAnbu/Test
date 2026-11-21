"""Ajedrez local para dos jugadores, sin dependencias externas."""

import argparse
from dataclasses import dataclass, field
import re


FILES = "abcdefgh"
RANKS = "12345678"
ROOKS = {"e1": ("a1", "h1"), "e8": ("a8", "h8")}


def square(file, rank):
    return FILES[file] + RANKS[rank]


def coordinates(cell):
    return FILES.index(cell[0]), RANKS.index(cell[1])


def initial_board():
    board = {}
    for rank, pieces in [(0, "RNBQKBNR"), (1, "PPPPPPPP"),
                         (6, "pppppppp"), (7, "rnbqkbnr")]:
        board.update({square(file, rank): piece for file, piece in enumerate(pieces)})
    return board


def reaches(board, start, end):
    """Comprueba la geometría de ataque, sin considerar jaques."""
    if start == end:
        return False
    x, y = coordinates(start)
    ex, ey = coordinates(end)
    dx, dy = ex - x, ey - y
    piece = board[start]
    kind = piece.lower()
    if kind == "p":
        return abs(dx) == 1 and dy == (1 if piece.isupper() else -1)
    if kind == "n":
        return sorted((abs(dx), abs(dy))) == [1, 2]
    if kind == "k":
        return max(abs(dx), abs(dy)) == 1
    diagonal = abs(dx) == abs(dy)
    straight = dx == 0 or dy == 0
    if not ((kind in "bq" and diagonal) or (kind in "rq" and straight)):
        return False
    step_x = (dx > 0) - (dx < 0)
    step_y = (dy > 0) - (dy < 0)
    return all(square(x + step_x * step, y + step_y * step) not in board
               for step in range(1, max(abs(dx), abs(dy))))


def attacked(board, end, by_white):
    return any(piece.isupper() == by_white and reaches(board, start, end)
               for start, piece in board.items())


@dataclass
class Game:
    board: dict = field(default_factory=initial_board)
    white: bool = True
    castling: set = field(default_factory=lambda: {"a1", "h1", "a8", "h8"})
    en_passant: str | None = None

    def in_check(self, board=None):
        board = self.board if board is None else board
        king = "K" if self.white else "k"
        cell = next(cell for cell, piece in board.items() if piece == king)
        return attacked(board, cell, not self.white)

    def after(self, start, end, promotion="q"):
        piece = self.board.get(start)
        target = self.board.get(end)
        if not piece or piece.isupper() != self.white:
            return None
        if target and (target.isupper() == self.white or target.lower() == "k"):
            return None

        x, y = coordinates(start)
        ex, ey = coordinates(end)
        board = self.board.copy()
        if piece.lower() == "p":
            direction = 1 if self.white else -1
            if x == ex and not target:
                double = (y == (1 if self.white else 6) and
                          ey - y == 2 * direction and
                          square(x, y + direction) not in board)
                if ey - y != direction and not double:
                    return None
            elif reaches(board, start, end):
                if not target:
                    if end != self.en_passant:
                        return None
                    del board[square(ex, y)]
            else:
                return None
            if ey in (0, 7):
                piece = promotion.upper() if self.white else promotion
        elif piece.lower() == "k" and y == ey and abs(ex - x) == 2:
            if start not in ROOKS:
                return None
            left, right = ROOKS[start]
            rook = left if ex < x else right
            rook_x, _ = coordinates(rook)
            if rook not in self.castling or any(
                square(file, y) in board
                for file in range(min(x, rook_x) + 1, max(x, rook_x))
            ):
                return None
            middle = square((x + ex) // 2, y)
            transit = board.copy()
            transit[middle] = transit.pop(start)
            if self.in_check() or self.in_check(transit):
                return None
            board[middle] = board.pop(rook)
        elif not reaches(board, start, end):
            return None

        del board[start]
        board[end] = piece
        return None if self.in_check(board) else board

    def play(self, move):
        match = re.fullmatch(r"([a-h][1-8])\s*([a-h][1-8])([qrbn])?", move)
        if not match:
            return False
        start, end, promotion = match.groups()
        piece = self.board.get(start, "")
        if promotion and (piece.lower() != "p" or end[1] not in "18"):
            return False
        board = self.after(start, end, promotion or "q")
        if board is None:
            return False
        self.castling.difference_update((start, end))
        if piece.lower() == "k":
            self.castling.difference_update(ROOKS.get(start, ()))
        x, y = coordinates(start)
        _, ey = coordinates(end)
        self.en_passant = (square(x, (y + ey) // 2)
                           if piece.lower() == "p" and abs(ey - y) == 2 else None)
        self.board = board
        self.white = not self.white
        return True

    def has_legal_move(self):
        return any(self.after(start, file + rank) is not None
                   for start, piece in self.board.items()
                   if piece.isupper() == self.white
                   for file in FILES for rank in RANKS)

    def show(self):
        for rank in reversed(RANKS):
            print(rank, " ".join(self.board.get(file + rank, ".") for file in FILES))
        print(" ", " ".join(FILES))


def main(argv=None):
    from partida import Partida

    parser = argparse.ArgumentParser(description="Juega al ajedrez en la terminal.")
    parser.add_argument("--cpu", nargs="?", const="negras",
                        choices=("blancas", "negras"),
                        help="juega contra la máquina (negras por defecto)")
    args = parser.parse_args(argv)

    partida = Partida(args.cpu)
    if args.cpu:
        print(f"La máquina juega con {args.cpu}.")
    print("Escribe e2e4 para mover, pista, deshacer o salir.")
    print("Mayúsculas: blancas. Promoción: añade q, r, b o n (dama por defecto).")
    while True:
        partida.game.show()
        player = partida.player
        status = partida.status()
        if status != "jugando":
            winner = "Negras" if partida.game.white else "Blancas"
            print(f"Jaque mate. Ganan {winner}." if status == "jaque_mate" else "Tablas por ahogado.")
            return
        if partida.game.in_check():
            print("Jaque.")
        if partida.cpu_turn():
            print(f"Máquina ({player}): {partida.cpu_move()}")
            continue
        try:
            move = input(f"{player}> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if move == "salir":
            return
        if move == "pista":
            print(f"Pista: {partida.hint()}")
        elif move == "deshacer":
            if not partida.undo():
                print("Nada que deshacer.")
        elif not partida.play(move):
            print("Movimiento ilegal. Inténtalo de nuevo.")


if __name__ == "__main__":
    main()
