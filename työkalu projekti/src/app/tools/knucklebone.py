import tkinter as tk
from tkinter import ttk
import random
from collections import Counter

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Knucklebone:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Knucklebones")
        self.root.geometry("400x610")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        # -------- STATE -------- #
        self.player_board = [[], [], []]
        self.ai_board = [[], [], []]
        self.canplay = True
        self.turn = "player"
        self.current_roll = None
        self.ai_difficulty = "medium"  # default difficulty
        # Status text shown in the UI (e.g., after starting a new game).
        self.status = "| Roll to start playing"
        # Track game sessions so pending AI moves from old games are ignored.
        self.game_id = 0
        self.ai_after_id = None

        # -------- UI -------- #
        title = tk.Label(root, text="Knucklebones", font=("Arial", 16, "bold"))
        title.pack(pady=5)

        # AI grid
        tk.Label(root, text="AI", font=("Arial", 12)).pack()
        self.ai_frame = tk.Frame(root)
        self.ai_frame.pack(pady=5)
        # makes 3x3 grid of labels for ai
        self.ai_cells = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                lbl = tk.Label(self.ai_frame, text="", width=4, height=2,
                               borderwidth=2, relief="ridge", font=("Arial", 12))
                lbl.grid(row=r, column=c, padx=2, pady=2)
                self.ai_cells[r][c] = lbl

        # Player grid
        tk.Label(root, text="Player", font=("Arial", 12)).pack()
        self.player_frame = tk.Frame(root)
        self.player_frame.pack(pady=5)

        self.player_cells = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                lbl = tk.Label(self.player_frame, text="", width=4, height=2,
                               borderwidth=2, relief="ridge", font=("Arial", 12))
                lbl.grid(row=r, column=c, padx=2, pady=2)
                self.player_cells[r][c] = lbl

        # Roll + score
        self.info_label = tk.Label(root, text="Roll: ", font=("Arial", 12))
        self.info_label.pack(pady=5)

        self.roll_button = tk.Button(root, text="Roll Dice", command=self.roll_dice)
        self.roll_button.pack(pady=5)
         # Column buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        #start game
        self.startbtn = tk.Button(root, text="Start New Game", command=self.startnewgame)
        self.startbtn.pack(pady=5)
        # AI Difficulty selector
        tk.Label(root, text="AI Difficulty:").pack(pady=5)
        self.difficulty_box = ttk.Combobox(root, values=["easy", "medium", "hard"], state="readonly")
        self.difficulty_box.set(self.ai_difficulty)
        self.difficulty_box.pack(pady=5)
        self.difficulty_box.bind("<<ComboboxSelected>>", self.set_difficulty)

       

        for i in range(3):
            btn = tk.Button(self.button_frame, text=f"Column {i+1}",
                            command=lambda i=i: self.place_player(i))
            btn.grid(row=0, column=i, padx=5)

        self.update_ui()
    def startnewgame(self):
        self._cancel_pending_ai_move()
        self.game_id += 1
        self.player_board = [[], [], []]
        self.ai_board = [[], [], []]
        self.roll_button.config(state="normal")
        self.turn = "player"
        self.canplay = False
        self.current_roll = None
        # Reset status when starting a new game.
        self.status = "| New game started"
        self.update_ui()

    def altstartnewgame(self):
        self._cancel_pending_ai_move()
        self.game_id += 1
        self.player_board = [[], [], []]
        self.ai_board = [[], [], []]
        self.roll_button.config(state="normal")
        self.turn = "player"
        self.current_roll = None
        # Reset status when starting a new game.
        self.status = "| Roll to start playing"
        self.canplay = False
        self.update_ui()
    #        DIFFICULTY
    def set_difficulty(self, event):
        self.ai_difficulty = self.difficulty_box.get()
        print("AI difficulty set to:", self.ai_difficulty)
        self.altstartnewgame()

    #          GAME LOGIC
    #  rolls dice on players turn  
    def roll_dice(self):
        self.status = ""
        if self.turn != "player":
           
            return

        self.current_roll = random.randint(1, 6)
        self.roll_button.config(state="disabled")
        self.update_ui()
    # places player dice on the selected available column
    def place_player(self, col):
        # if not players turn or no current number on roll return nothing
        if self.turn != "player" or self.current_roll is None:
            return
        #if a line has more than or exactly 3, return nothing  
        if len(self.player_board[col]) >= 3:
            return

        value = self.current_roll
        self.player_board[col].append(value)
        # Destroy matches in AI column
        self.ai_board[col] = [x for x in self.ai_board[col] if x != value]

        self.current_roll = None
        self.update_ui()

        if self.is_full(self.player_board) or self.is_full(self.ai_board):
            self.end_game()
            return

        self.turn = "ai"
        self.turn_text = "AI's turn"
        self.update_ui()
        self.canplay = True
        self.ai_turn()
    def ai_turn(self):
        roll = random.randint(1, 6)

        valid_cols = [i for i in range(3) if len(self.ai_board[i]) < 3]
        if not valid_cols:
            return

        # AI STRATEGY
        # Easy: pick a random valid column.
        # Medium: prioritize destroying player's matching dice.
        # Hard: balance destruction, stacking same rolls, and column height.
        if self.ai_difficulty == "easy":
            # random choice
            col = random.choice(valid_cols)
        else:
            best_cols = []
            best_score = -1
            for i in valid_cols:
                # How many player dice would be destroyed by placing here.
                destroy_count = sum(1 for x in self.player_board[i] if x == roll)
                # How many of AI's dice already match this roll (stacking value).
                self_count = self.ai_board[i].count(roll)
                # Penalize tall columns so AI spreads when needed.
                col_height = len(self.ai_board[i])

                if self.ai_difficulty == "medium":
                    # Medium only cares about destruction.
                    score = destroy_count
                elif self.ai_difficulty == "hard":
                    # Hard balances destruction, stacking, and column height.
                    score = destroy_count * 3 + self_count * 4 - col_height * 0.5
                    if self.player_board[i].count(roll) >= 2:
                        # Bonus for wiping out a double stack.
                        score += 2

                if score > best_score:
                    best_score = score
                    best_cols = [i]
                elif score == best_score:
                    best_cols.append(i)

            if best_score <= 0:
                # If all options are weak, prefer shorter columns.
                best_cols = sorted(valid_cols, key=lambda i: len(self.ai_board[i]))

            col = random.choice(best_cols)

        game_id = self.game_id

        def apply_ai_move():
            # Ignore stale AI moves from previous games or if turn changed.
            if game_id != self.game_id or self.turn != "ai" or not self.canplay:
                return

            # Delay the placement so the AI doesn't move instantly.
            self.ai_board[col].append(roll)
            # Destroy matches in player column
            self.player_board[col] = [x for x in self.player_board[col] if x != roll]
            self.roll_button.config(state="normal")

            self.update_ui()

            if self.is_full(self.player_board) or self.is_full(self.ai_board):
                self.end_game()
                return

            self.turn = "player"
            self.turn_text = "Your turn" if self.turn == "player" else "AI's turn"
            self.update_ui()

        # Add a short delay before committing the AI's move.
        self.ai_after_id = self.root.after(1200, apply_ai_move)

    def _cancel_pending_ai_move(self):
        if self.ai_after_id is None:
            return
        try:
            self.root.after_cancel(self.ai_after_id)
        except Exception:
            pass
        finally:
            self.ai_after_id = None
            
    #handle giving score and multipliers
    def score_board(self, board):
        total = 0
        for col in board:
            counts = Counter(col)
            for num, count in counts.items():
                multiplier = count if count >= 2 else 1
                total += num * count * multiplier
        return total

    def is_full(self, board):
        return all(len(col) >= 3 for col in board)

    def end_game(self):
        player_score = self.score_board(self.player_board)
        ai_score = self.score_board(self.ai_board)
        #calculate scores and decide winner
        if player_score > ai_score:
            result = f"You win on {self.ai_difficulty} mode!"
        elif ai_score > player_score:
            result = "AI wins!"
        else:
            result = "Draw!"

        self.info_label.config(text=f"{result} ({player_score}-{ai_score})")
        #disable roll button at the end of the game
        self.roll_button.config(state="disabled")

    # -------- UI UPDATE -------- #
    def update_ui(self):
        # Clear grids
        for r in range(3):
            for c in range(3):
                self.player_cells[r][c].config(text="")
                self.ai_cells[r][c].config(text="")

        # Draw player board
        for c in range(3):
            for i, val in enumerate(self.player_board[c]):
                r = 2 - i
                self.player_cells[r][c].config(text=str(val))

        # Draw AI board
        for c in range(3):
            for i, val in enumerate(self.ai_board[c]):
                r = 2 - i
                self.ai_cells[r][c].config(text=str(val))

        # Update info
        player_score = self.score_board(self.player_board)
        ai_score = self.score_board(self.ai_board)

        roll_text = self.current_roll if self.current_roll else ""
        turn_text = "Your turn" if self.turn == "player" else "AI's turn"

        # Show status in the info line so new-game state is visible.
        self.info_label.config(
            text=f"Roll: {roll_text} | {turn_text} | player {player_score}-{ai_score} Ai  {self.status}"
        )


def run():
    root = tk.Tk()
    Knucklebone(root)
    root.mainloop()


if __name__ == "__main__":
    run()
