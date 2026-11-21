"""Interfaz gráfica del ajedrez local."""

import tkinter as tk
from tkinter import ttk

from ajedrez import FILES, RANKS
from partida import Partida


BG = "#141c1a"
PANEL = "#202d29"
INK = "#f4eedf"
MUTED = "#b7c4b9"
ACCENT = "#e9bd75"
LIGHT = "#e6d9be"
DARK = "#729182"
PIECES = dict(zip("kqrbnp", "♚♛♜♝♞♟"))
MODES = {"Dos jugadores": None, "Máquina con negras": "negras",
         "Máquina con blancas": "blancas"}


class ChessWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ajedrez")
        self.root.geometry("940x690")
        self.root.minsize(720, 530)
        self.root.configure(bg=BG)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Chess.TButton", background=ACCENT, foreground=BG,
                        font=("DejaVu Sans", 10, "bold"), padding=(10, 8))
        style.map("Chess.TButton", background=[("disabled", "#46544e"),
                                                ("active", "#f9d195")])
        style.configure("Chess.TCombobox", padding=5, font=("DejaVu Sans", 10))

        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(18, 8), pady=18)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<Button-1>", self.click)

        side = tk.Frame(root, bg=PANEL, padx=22, pady=28)
        side.grid(row=0, column=1, sticky="ns", padx=(8, 22), pady=24)
        side.columnconfigure(0, weight=1)
        self.label(side, "Ajedrez", INK, ("DejaVu Serif", 29), 0)
        self.status = self.label(side, "", INK, ("DejaVu Sans", 14, "bold"), 1,
                                 pady=(26, 6))
        self.detail = self.label(side, "", MUTED, ("DejaVu Sans", 10), 2,
                                 pady=(0, 24))
        self.label(side, "Modo de juego", MUTED, ("DejaVu Sans", 10), 3)
        self.mode = ttk.Combobox(side, values=list(MODES), state="readonly",
                                 style="Chess.TCombobox", width=22)
        self.mode.current(0)
        self.mode.grid(row=4, column=0, sticky="ew", pady=(6, 10))
        self.button(side, "Nueva partida", self.new_game, 5)
        self.hint_button = self.button(side, "Pista", self.hint, 6)
        self.undo_button = self.button(side, "Deshacer", self.undo, 7)
        self.label(
            side, "Coronar como", MUTED, ("DejaVu Sans", 10), 8, pady=(12, 0))
        self.promotion = ttk.Combobox(side, values=("Dama", "Torre", "Alfil", "Caballo"),
                                      state="readonly", style="Chess.TCombobox")
        self.promotion.current(0)
        self.promotion.grid(row=9, column=0, sticky="ew", pady=(6, 0))
        self.new_game()

    @staticmethod
    def label(parent, text, color, font, row, **grid):
        label = tk.Label(parent, text=text, bg=PANEL, fg=color, font=font,
                         anchor="w", justify="left", wraplength=200)
        label.grid(row=row, column=0, sticky="ew", **grid)
        return label

    @staticmethod
    def button(parent, text, command, row):
        button = ttk.Button(parent, text=text, command=command, style="Chess.TButton")
        button.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        return button

    @property
    def game(self):
        return self.partida.game

    def new_game(self):
        if getattr(self, "pending", None) is not None:
            self.root.after_cancel(self.pending)
        self.pending = None
        self.cpu = MODES[self.mode.get()]
        self.partida = Partida(self.cpu)
        self.selected = None
        self.suggestion = None
        self.last_move = None
        self.refresh()

    def refresh(self, note=""):
        status = self.partida.status()
        self.finished = status != "jugando"
        side = self.partida.player
        machine_turn = not self.finished and side.lower() == self.cpu
        if self.finished:
            winner = "Negras" if self.game.white else "Blancas"
            title = f"Ganan {winner.lower()}" if status == "jaque_mate" else "Tablas"
            note = "Jaque mate" if status == "jaque_mate" else "Ahogado"
        elif machine_turn:
            title, note = "Turno de la máquina", "Pensando…"
            if self.pending is None:
                self.pending = self.root.after(40, self.machine_move)
        else:
            title = f"Turno de {side.lower()}"
            note = note or ("Jaque" if self.game.in_check() else "Selecciona una pieza.")
        self.status.configure(text=title)
        self.detail.configure(text=note)
        self.hint_button.state(["disabled" if self.finished or machine_turn else "!disabled"])
        self.undo_button.state(["!disabled" if self.partida.can_undo()
                                else "disabled"])
        self.draw()

    def board_geometry(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        size = max(1, (min(width, height) - 44) // 8)
        return (width - size * 8) // 2, (height - size * 8) // 2, size

    def axes(self):
        if self.cpu == "blancas":
            return FILES[::-1], RANKS
        return FILES, RANKS[::-1]

    def draw(self):
        canvas = self.canvas
        canvas.delete("all")
        left, top, size = self.board_geometry()
        files, ranks = self.axes()
        for row, rank in enumerate(ranks):
            y = top + row * size
            canvas.create_text(left - 13, y + size / 2, text=rank, fill=MUTED,
                               font=("DejaVu Sans", 10))
            for col, file in enumerate(files):
                x = left + col * size
                cell = file + rank
                color = DARK if (row + col) % 2 else LIGHT
                if self.last_move and cell in (self.last_move[:2], self.last_move[2:4]):
                    color = "#b5b377" if (row + col) % 2 else "#ded394"
                if self.suggestion and cell in (self.suggestion[:2], self.suggestion[2:4]):
                    color = "#92bab7"
                if cell == self.selected:
                    color = ACCENT
                canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="")
                piece = self.game.board.get(cell)
                if piece:
                    font = ("DejaVu Sans", max(1, int(size * .67)), "bold")
                    for offset in (-1, 1):
                        canvas.create_text(x + size / 2 + offset, y + size / 2 + 1,
                                           text=PIECES[piece.lower()], font=font,
                                           fill="#182924")
                    canvas.create_text(x + size / 2, y + size / 2,
                                       text=PIECES[piece.lower()], font=font,
                                       fill="#fff5df" if piece.isupper() else "#23352f")
                if self.selected and self.game.after(self.selected, cell) is not None:
                    radius = size / 10
                    cx, cy = x + size / 2, y + size / 2
                    if piece:
                        canvas.create_rectangle(x + 3, y + 3, x + size - 3, y + size - 3,
                                                width=3, outline=ACCENT)
                    else:
                        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                           fill="#3a5a4c", outline="")
                if row == 7:
                    canvas.create_text(x + size / 2, top + 8 * size + 14,
                                       text=file, fill=MUTED, font=("DejaVu Sans", 10))

    def click(self, event):
        if self.finished or self.partida.player.lower() == self.cpu:
            return
        left, top, size = self.board_geometry()
        col, row = (event.x - left) // size, (event.y - top) // size
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        files, ranks = self.axes()
        cell = files[col] + ranks[row]
        piece = self.game.board.get(cell)
        self.suggestion = None
        if piece and piece.isupper() == self.game.white:
            self.selected = None if self.selected == cell else cell
            self.refresh()
        elif self.selected:
            move = self.selected + cell
            if self.game.board[self.selected].lower() == "p" and cell[1] in "18":
                move += "qrbn"[self.promotion.current()]
            if self.partida.play(move):
                self.last_move = move
                self.selected = None
                self.refresh()
            else:
                self.refresh("Movimiento ilegal.")

    def machine_move(self):
        self.pending = None
        try:
            self.last_move = self.partida.cpu_move()
        except RuntimeError:
            self.detail.configure(text="La máquina no pudo mover.")
        else:
            self.refresh()

    def hint(self):
        move = self.partida.hint()
        if move:
            self.suggestion = move
            self.refresh(f"Pista · {move[:2]} → {move[2:4]}{move[4:]}")

    def undo(self):
        if self.partida.undo():
            if self.pending is not None:
                self.root.after_cancel(self.pending)
                self.pending = None
            self.last_move = self.selected = self.suggestion = None
            self.refresh("Jugada deshecha.")


def main():
    root = tk.Tk()
    ChessWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
