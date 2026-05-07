import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import datetime
import json

from src.app.tools.autoclicker import AutoClicker
from src.app.tools.colourseekingcursor import ColourSeekingCursor
from src.app.tools.Multiplyby2 import multiplyby2
from src.app.tools.stopwatch import Stopwatch
from src.app.tools.numberguesser import NumberGuesser
from src.app.tools.pwned import PwnedPasswordChecker
from src.app.tools.knucklebone import Knucklebone
from src.app.tools.calc import Calc
from src.app.tools.musicfile import MusicFile
from src.app.tools.write import Write
from src.app.tools.randomwalk import RandomWalk
from src.app.tools.passgen import PasswordGenerator
from src.app.tools.tictatactoe import TicTacToeGame
from src.app.tools.rps import RpsGame
from src.app.tools.unit import Unit
from src.app.tools.kmh import Kmh

_OPEN_WINDOWS = {}
_PONG_PROCESS = None



def create_ui(root):
    """Create the main UI with 2-column tool layout"""

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = ttk.Label(main_frame, text="Tool Kit", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)

    # ================= MAIN TOOLS =================
    ttk.Label(main_frame, text="Main tools", font=("Arial", 16, "bold")).pack(pady=10)

    main_tools_frame = ttk.Frame(main_frame)
    main_tools_frame.pack(fill=tk.BOTH, expand=True)

    main_tools = [
        ("Auto Clicker", open_autoclicker_window, "Auto Clicker info", "Automatically clicks at a configurable speed."),
        ("Colour Seeking Cursor", open_colourseekingcursor_window, "Cursor info", "Moves cursor toward a target color."),
        ("Stopwatch", open_stopwatch_window, "Stopwatch info", "Simple stopwatch."),
        ("Calculator", open_calc_window, "Calculator info", "Basic arithmetic calculator."),
        ("Music File", open_musicfile_window, "Music info", "Play MP3 files."),
        ("Write", open_write_window, "Write info", "Simple text editor."),
    ]

    _build_tool_grid(main_tools_frame, main_tools)

    # ================= IRRELEVANT TOOLS =================
    ttk.Label(main_frame, text="Irrelevant tools", font=("Arial", 12, "bold")).pack(pady=10)

    irrelevant_frame = ttk.Frame(main_frame)
    irrelevant_frame.pack(fill=tk.BOTH, expand=True)

    irrelevant_tools = [
        ("Pwned Passwords", open_pwned_passwords_window, "Pwned info", "Checks if password was leaked."),
        ("Password Generator", open_password_generator_window, "Gen info", "Generates secure passwords."),
        ("Multiply by 2", open_multiplyby2_window, "Multiply info", "Doubles a number."),
        ("Random Walk", open_template_window, "Random Walk info", "Infinite random movement simulation."),
        ("Unit Converter", open_unit_window, "Unit Converter info", "Converts between 2 different units of measurement."),
        ("Kilometers Per Hour", open_kmh_window, "KMH info", "simulates distance traveled based on a constant speed."),
       
    ]

    _build_tool_grid(irrelevant_frame, irrelevant_tools)

    # ================= MINI GAMES =================
    ttk.Label(main_frame, text="Mini games", font=("Arial", 12, "bold")).pack(pady=10)

    games_frame = ttk.Frame(main_frame)
    games_frame.pack(fill=tk.BOTH, expand=True)

    games_tools = [
        ("Pong", open_pong_window, "Pong info", "Classic arcade paddle game."),
        ("Knucklebones", open_knucklebone_window, "Knucklebone info", "Dice strategy game."),
        ("Number Guesser", open_number_guesser_window, "Guess info", "Guess the secret number."),
        ("Tic Tac Toe", open_minigame_template_window, "Tic Tac Toe info", "Classic Tic Tac Toe game."),
        ("Rock Paper Scissors", open_rps_window, "Rock Paper Scissors info", "Play Rock Paper Scissors against the computer."),
    ]

    _build_tool_grid(games_frame, games_tools)

    # ================= CLOCK =================
    timelabel = ttk.Label(main_frame, text="")
    timelabel.pack(pady=15)
    update_time_label(timelabel)

    return main_frame


def _build_tool_grid(parent, tools):
    """Build 2-column grid layout for tools"""
    for index, (label, command, info_title, info_text) in enumerate(tools):
        row = index // 2
        col = index % 2

        frame = ttk.Frame(parent, padding=5)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        parent.grid_columnconfigure(col, weight=1)

        tool_btn = ttk.Button(frame, text=label, command=command)
        tool_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        info_btn = ttk.Button(
            frame,
            text="ⓘ",
            width=3,
            command=lambda t=info_title, x=info_text: messagebox.showinfo(t, x),
        )
        info_btn.pack(side=tk.LEFT, padx=(8, 0))


def update_time_label(label):
    now = datetime.datetime.now()
    label.config(text=now.strftime("%d-%m-%Y %H:%M:%S"))
    label.after(100, update_time_label, label)


# ================= WINDOW HANDLING =================

def _bring_window_to_front(window):
    window.deiconify()
    window.lift()
    try:
        window.focus_force()
    except tk.TclError:
        window.focus_set()


def _open_singleton_window(key, builder):
    existing = _OPEN_WINDOWS.get(key)
    if existing is not None and existing.winfo_exists():
        _bring_window_to_front(existing)
        return existing

    window = tk.Toplevel()
    _OPEN_WINDOWS[key] = window

    def _cleanup(event):
        if event.widget is window:
            _OPEN_WINDOWS.pop(key, None)

    window.bind("<Destroy>", _cleanup, add="+")
    builder(window)
    return window


# ================= TOOL OPENERS =================

def open_password_generator_window():
    _open_singleton_window("password_generator", PasswordGenerator)

def open_autoclicker_window():
    _open_singleton_window("autoclicker", AutoClicker)

def open_number_guesser_window():
    _open_singleton_window("number_guesser", NumberGuesser)

def open_colourseekingcursor_window():
    _open_singleton_window("colourseekingcursor", ColourSeekingCursor)

def open_stopwatch_window():
    _open_singleton_window("stopwatch", Stopwatch)

def open_calc_window():
    _open_singleton_window("calc", Calc)

def open_pwned_passwords_window():
    _open_singleton_window("pwned_passwords", PwnedPasswordChecker)

def open_musicfile_window():
    _open_singleton_window("musicfile", MusicFile)

def open_write_window():
    _open_singleton_window("write", Write)

def open_template_window():
    _open_singleton_window("template", RandomWalk)

def open_multiplyby2_window():
    _open_singleton_window("multiplyby2", multiplyby2)

def open_unit_window():
    _open_singleton_window("unit", Unit)

def open_knucklebone_window():
    _open_singleton_window("knucklebone", Knucklebone)

def open_minigame_template_window():
    _open_singleton_window("minigame_template", TicTacToeGame)

def open_kmh_window():
    _open_singleton_window("kmh", Kmh)

def open_rps_window():
    _open_singleton_window("rps", RpsGame)




def open_pong_window():
    global _PONG_PROCESS
    try:
        if _PONG_PROCESS is not None and _PONG_PROCESS.poll() is None:
            return

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )

        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--pong"]
        else:
            cmd = [sys.executable, "-m", "src.app.tools.pong"]

        _PONG_PROCESS = subprocess.Popen(cmd, cwd=project_root)

    except Exception as e:
        _PONG_PROCESS = None
        messagebox.showerror("Pong", f"Failed to launch Pong:\n{e}")
