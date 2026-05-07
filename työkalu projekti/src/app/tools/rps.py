"""Simple Rock Paper Scissors minigame."""

import random
import tkinter as tk
from tkinter import ttk

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class RpsGame:
    """Play Rock Paper Scissors against the computer."""

    CHOICES = ("🪨Rock🪨", "📄Paper📄", "✄Scissors✄")

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Rock Paper Scissors")
        self.root.geometry("420x340")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        self.player_score = 0
        self.computer_score = 0
        self.best_of = 3
        self.game_over = False
        self.result_var = tk.StringVar(value="Choose Rock, Paper, or Scissors to start.")
        self.score_var = tk.StringVar(value=self._score_text())
        self.choice_var = tk.StringVar(value="Your move: -\nComputer move: -")
        
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Rock Paper Scissors",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 8))

        self.title_label = ttk.Label(
            container,
            text=f"Play against the computer in a quick best-of-{self.best_of} match.",
            wraplength=340,
            justify="center",
        )
        self.title_label.pack(pady=(0, 12))

        button_row = ttk.Frame(container)
        button_row.pack(pady=(0, 12))

        for choice in self.CHOICES:
            ttk.Button(
                button_row,
                text=choice,
                command=lambda selected=choice: self.play_round(selected),
            ).pack(side=tk.LEFT, padx=4)

        ttk.Label(
            container,
            textvariable=self.choice_var,
            justify="center",
        ).pack(pady=(0, 10))

        ttk.Label(
            container,
            textvariable=self.result_var,
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 10))

        ttk.Label(
            container,
            textvariable=self.score_var,
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=(0, 12))
        ttk.Label(
            container,
            text="best of:",
            font=("Segoe UI", 9),
        ).pack(pady=(0, 4))
        self.best_of_entry = ttk.Entry(container, state="normal", justify="center")
        self.best_of_entry.pack(pady=(0, 12))
        self.best_of_entry.insert(0, int(self.best_of))
        self.best_of_entry.bind("<KeyRelease>", self.get_best_of)

        ttk.Button(container, text="Start a new Game", command=self.reset_score).pack()

    def _score_text(self):
        return f"Score: You {self.player_score} - {self.computer_score} Computer"
    
    def get_best_of(self, event):
         self.best_of = int(self.best_of_entry.get())
         self.title_label.config(text=f"Play against the computer in a quick best-of-{self.best_of} match.")
         self.reset_score()
         


    def play_round(self, player_choice):
        if self.game_over:
            self.result_var.set("Game over. Please start a new game to play again.")
            return
        else:
            computer_choice = random.choice(self.CHOICES)
        self.choice_var.set(
            f"Your move: {player_choice}\nComputer move: {computer_choice}"
        )

        if player_choice == computer_choice:
            self.result_var.set("Tie round.")
        elif (
            (player_choice == "🪨Rock🪨" and computer_choice == "✄Scissors✄")
            or (player_choice == "📄Paper📄" and computer_choice == "🪨Rock🪨")
            or (player_choice == "✄Scissors✄" and computer_choice == "📄Paper📄")
        ):
            self.player_score += 1 
            self.result_var.set("You win this round.")
            if self.player_score >= self.best_of // 2 + 1:
                self.end_game()
                
        else:
            
            self.computer_score += 1
           
            self.result_var.set("Computer wins this round.")
            if self.computer_score >= self.best_of // 2 + 1:
                self.end_game()
        

        self.score_var.set(self._score_text())
    def end_game(self):
        self.game_over = True
        if self.player_score > self.computer_score:
            self.result_var.set("Congratulations! You won the game!")
            
        elif self.computer_score > self.player_score:
            self.result_var.set("Computer wins the game. Better luck next time!")
            
        else:
            self.result_var.set("The game is a tie!")
            

    
    def reset_score(self):
        self.game_over = False
        self.player_score = 0
        self.computer_score = 0
        self.choice_var.set("Your move: -\nComputer move: -")
        self.result_var.set("Choose Rock, Paper, or Scissors to start.")
        self.score_var.set(self._score_text())


def run():
    """Launch the Rock Paper Scissors tool."""
    root = tk.Tk()
    RpsGame(root)
    root.mainloop()


if __name__ == "__main__":
    run()
