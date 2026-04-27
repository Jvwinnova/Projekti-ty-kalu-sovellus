"""Local two-player Tic Tac Toe played in a single window."""

import tkinter as tk
from tkinter import ttk, messagebox

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class TicTacToeGame:
    """Manage board state, turns, and win detection for Tic Tac Toe."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.resizable(False, False)

        apply_app_icon(self.root)

        self.player = "X" # X always starts
        self.stop_game = False # Flag to indicate if the game has ended
        # 0 = empty, 1 = X, 2 = O
        self.states = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

        self.buttons = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0)

        ttk.Label(
            container,
            text="Tic Tac Toe",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # board
        board = ttk.Frame(container)
        board.grid(row=1, column=0, columnspan=3)

        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    board,
                    text="",
                    font=("Helvetica", 20),
                    width=5,
                    height=2,
                    command=lambda r=i, c=j: self.clicked(r, c)
                )
                btn.grid(row=i, column=j)
                self.buttons[i][j] = btn

        ttk.Button(
            container,
            text="Reset",
            command=self.reset_game
        ).grid(row=2, column=0, columnspan=3, pady=(10, 0))

    # ---------------- GAME LOGIC ----------------
    def clicked(self, r, c):
        """Handle a player's move when a board button is pressed."""
        if self.stop_game:
            return

        if self.states[r][c] != 0:
            return

        self.states[r][c] = self.player
        self.buttons[r][c].config(text=self.player)

        self.check_win()

        if not self.stop_game:
            self.player = "O" if self.player == "X" else "X"

    def check_win(self):
        """Check rows, columns, diagonals, and tie state after each move."""
        s = self.states

        # rows + columns
        for i in range(3):
            if s[i][0] == s[i][1] == s[i][2] != 0:
                self.win(s[i][0])
                return

            if s[0][i] == s[1][i] == s[2][i] != 0:
                self.win(s[0][i])
                return

        # diagonals
        if s[0][0] == s[1][1] == s[2][2] != 0:
            self.win(s[0][0])
            return

        if s[0][2] == s[1][1] == s[2][0] != 0:
            self.win(s[0][2])
            return

        # tie
        if all(s[i][j] != 0 for i in range(3) for j in range(3)):
            self.stop_game = True
            messagebox.showinfo("Tie", "It's a tie!")

    def win(self, player):
        """End the game and announce the winning player."""
        self.stop_game = True
        messagebox.showinfo("Winner", f"{player} Wins!")

    # ---------------- RESET ----------------
    def reset_game(self):
        """Clear the board and reset turn order to the starting player."""
        self.player = "X"
        self.stop_game = False

        for i in range(3):
            for j in range(3):
                self.states[i][j] = 0
                self.buttons[i][j].config(text="")


# ---------------- RUN FUNCTION ----------------
def run():
    """Launch the Tic Tac Toe tool."""
    root = tk.Tk()
    TicTacToeGame(root)
    root.mainloop()


if __name__ == "__main__":
    run()
