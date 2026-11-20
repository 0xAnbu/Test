"""Rival automático para ajedrez.py: minimax (negamax) con poda alfa-beta."""

from ajedrez import FILES, RANKS, Game, coordinates

VALUES = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}
MATE = 100_000


def legal_moves(game):
    """Todas las jugadas legales del bando que mueve, en notación UCI."""
    moves = []
    for start, piece in sorted(game.board.items()):
        if piece.isupper() != game.white:
            continue
        for end in (f + r for f in FILES for r in RANKS):
            target = game.board.get(end)
            if target and target.isupper() == game.white:
                continue
            if game.after(start, end) is None:
                continue
            if piece.lower() == "p" and end[1] in "18":
                moves += [start + end + p for p in "qrbn"]
            else:
                moves.append(start + end)
    return moves


def _child(game, move):
    child = Game(board=game.board.copy(), white=game.white,
                 castling=set(game.castling), en_passant=game.en_passant)
    child.play(move)
    return child


def evaluate(game):
    """Puntuación desde el punto de vista del bando que mueve."""
    score = 0
    for cell, piece in game.board.items():
        x, y = coordinates(cell)
        kind = piece.lower()
        value = VALUES[kind]
        if kind in "nbp":
            value += int(6 - abs(3.5 - x) - abs(3.5 - y)) * 4
        if kind == "p":
            value += 5 * (y - 1 if piece.isupper() else 6 - y)
        score += value if piece.isupper() else -value
    return score if game.white else -score


def _order(game, moves):
    """Capturas primero (más valiosas antes) para podar más."""
    return sorted(moves, key=lambda m: -VALUES.get(game.board.get(m[2:4], "k").lower(), 0))


def _negamax(game, depth, alpha, beta, ply):
    if depth == 0:
        if game.has_legal_move():
            return evaluate(game)
        return -(MATE - ply) if game.in_check() else 0
    moves = legal_moves(game)
    if not moves:
        return -(MATE - ply) if game.in_check() else 0
    for move in _order(game, moves):
        score = -_negamax(_child(game, move), depth - 1, -beta, -alpha, ply + 1)
        if score >= beta:
            return score
        alpha = max(alpha, score)
    return alpha


def best_move(game, depth=3):
    """Mejor jugada según la búsqueda, o None si no hay jugadas legales. Determinista."""
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("depth debe ser un entero positivo")
    moves = legal_moves(game)
    if not moves:
        return None
    best, alpha = None, -MATE - 1
    for move in _order(game, moves):
        score = -_negamax(_child(game, move), depth - 1, -MATE - 1, -alpha, 1)
        if score > alpha:
            best, alpha = move, score
    return best
