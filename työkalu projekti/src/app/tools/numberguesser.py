import random
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class NumberGuesser:
    """Simple number guessing game."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Number Guesser")
        self.root.geometry("700x340")
        self.root.resizable(False, False)
        apply_app_icon(self.root)
        self.has_won = False
        self.min_value = 1
        self.max_value = 100
        self.max_attempts = 10
        self._new_game()
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Number Guesser",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 6))

        self.rules_label = ttk.Label(
            container,
            text=self._rules_text(),
            wraplength=320,
        )
        self.rules_label.pack(pady=(0, 10))

        entry_row = ttk.Frame(container)
        entry_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(entry_row, text="Your guess:").pack(side=tk.LEFT)
        self.guess_var = tk.StringVar()
        self.guess_entry = ttk.Entry(entry_row, textvariable=self.guess_var, width=12)
        self.guess_entry.pack(side=tk.LEFT, padx=(8, 0))
        self.guess_entry.bind("<Return>", self._on_guess)
        
        ttk.Label(entry_row, text="Max attempts:").pack(side=tk.LEFT, padx=(80, 0))
        self.max_attempts_var = tk.StringVar()
        self.max_attempts_entry = ttk.Entry(entry_row, textvariable=self.max_attempts_var, width=12)
        self.max_attempts_entry.pack(side=tk.LEFT, padx=(8, 0))
        self.max_attempts_entry.bind("<Return>", self._on_max_attempts_change)

        ttk.Label(entry_row, text="Max range:").pack(side=tk.LEFT, padx=(0, 0))
        self.max_value_var = tk.StringVar()
        self.max_value_entry = ttk.Entry(entry_row, textvariable=self.max_value_var, width=12)
        self.max_value_entry.pack(side=tk.LEFT, padx=(8, 0))
        self.max_value_entry.bind("<Return>", self._on_range_change)

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(actions, text="Guess", command=self._on_guess).pack(side=tk.LEFT)
        ttk.Button(actions, text="New game", command=self._reset_game).pack(side=tk.LEFT, padx=(8, 0))

        self.feedback_var = tk.StringVar(value="Make a guess to start.")
        self.feedback_label = ttk.Label(container, textvariable=self.feedback_var, wraplength=320)
        self.feedback_label.pack(pady=(0, 8))

        self.attempts_var = tk.StringVar(value=self._attempts_text())
        ttk.Label(container, textvariable=self.attempts_var).pack()

    def _rules_text(self):
        return f"Guess a number between {self.min_value} and {self.max_value}."
    
    def _attempts_text(self):
        return f"Attempts left: {self.attempts_left}"
    
    def _on_range_change(self, event=None):
        
        # Example: get new max value from an entry or variable
        raw = self.max_value_var.get().strip() if hasattr(self, 'max_value_var') else ""
        try:
            new_maxvalue = int(raw)
            if new_maxvalue <= self.min_value:
                raise ValueError("Max value must be greater than min value.")
            self.max_value = new_maxvalue
            self.rules_label.config(text=self._rules_text())
            self._alternate_reset_game()
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid number greater than min value for max value.")
     


    def _on_max_attempts_change(self, event=None):
       
        raw = self.max_attempts_var.get().strip()
       
        if not raw:
            return

        try:
            new_max = int(raw)
            
            if new_max <= 0:
                raise ValueError("Max attempts must be positive.")
            
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a positive whole number for max attempts.")
            self.max_attempts_var.set(str(self.max_attempts))
            return

        self.max_attempts = new_max
        self._alternate_reset_game()
        

    def _new_game(self):
        self.secret = random.randint(self.min_value, self.max_value)
        self.attempts_left = self.max_attempts
        self.has_won = False

    def _alternate_reset_game(self):
        self._new_game()
        self.feedback_var.set("Make a guess to start.")
        self.attempts_var.set(self._attempts_text())
        self.guess_var.set("")
        self.guess_entry.focus_set()

    def _reset_game(self):
        self._new_game()
        self.feedback_var.set("New game started. Good luck!")
        self.attempts_var.set(self._attempts_text())
        self.guess_var.set("")
        self.guess_entry.focus_set()

    def _on_guess(self, event=None):
        if self.has_won:
            self.feedback_var.set("You've already won! Start a new game to play again.")
            return

        raw = self.guess_var.get().strip()
        if not raw:
            self.feedback_var.set("Enter a number and try again.")
            return

        try:
            guess = int(raw)
        except ValueError:
            self.feedback_var.set("That's not a whole number.")
            return

        if guess < self.min_value or guess > self.max_value:
            self.feedback_var.set(self._rules_text())
            return

        if self.attempts_left <= 0:
            self.feedback_var.set("No attempts left. Start a new game.")
            return

        self.attempts_left -= 1

        if guess == self.secret:
            self.feedback_var.set(f"Correct! You guessed the number {self.secret} with {self.max_attempts - self.attempts_left} attempts and {self.attempts_left} attempts remaining. with the range of {self.min_value} to {self.max_value}.")
            self.attempts_var.set(self._attempts_text())
            self.has_won = True
            return

        if guess < self.secret:
            self.feedback_var.set("Too low.")
        else:
            self.feedback_var.set("Too high.")

        if self.attempts_left == 0:
            self.feedback_var.set(f"Out of attempts! The number was {self.secret}.")

        self.attempts_var.set(self._attempts_text())
        


def run():
    root = tk.Tk()
    NumberGuesser(root)
    root.mainloop()


if __name__ == "__main__":
    run()
