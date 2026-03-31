import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from src.app.tools.autoclicker import AutoClicker
from src.app.tools.colourseekingcursor import ColourSeekingCursor
from src.app.tools.Multiplyby2 import multiplyby2
from src.app.tools.stopwatch import Stopwatch
from src.app.tools.numberguesser import NumberGuesser
from src.app.tools.pwned import PwnedPasswordChecker
from src.app.tools.knucklebone import Knucklebone
from src.app.tools.calc import Calc
from src.app.tools.musicfile import MusicFile
import datetime

_OPEN_WINDOWS = {}
_PONG_PROCESS = None

def create_ui(root):
    """Create the main UI with tabs for different tools"""
    # This function builds the main window layout and all tool buttons.

    # Create the main container frame for all widgets.
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Main app title.
    title_label = ttk.Label(main_frame, text="Tool Kit", font=("Arial", 18, "bold"))
    title_label.pack(pady=20)
    
    # Section title.
    title_label = ttk.Label(main_frame, text="Main tools", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)

    # Each tool row contains the main button plus a small info button.
    _add_tool_row(
        main_frame,
        label="Auto Clicker",
        command=open_autoclicker_window,
        info_title="Auto Clicker info",
        info_text="Automatically clicks at a configurable speed.",
    )

    _add_tool_row(
        main_frame,
        label="Colour Seeking Cursor",
        command=open_colourseekingcursor_window,
        info_title="Colour Seeking Cursor info",
        info_text="Moves the cursor toward a target color on screen.",
    )

    _add_tool_row(
        main_frame,
        label="Stopwatch",
        command=open_stopwatch_window,
        info_title="Stopwatch info",
        info_text="Simple stopwatch with start, stop, and reset.",
    )

    _add_tool_row(
        main_frame,
        label="Calculator",
        command=open_calc_window,
        info_title="Calculator info",
        info_text="A simple calculator for basic arithmetic operations.",
    )

    _add_tool_row(
        main_frame,
        label="Music File",
        command=open_musicfile_window,
        info_title="Music File info",
        info_text="Empty tool template wired to the UI.",
    )
    

    # Section title for tools that are less important.
    title_label = ttk.Label(main_frame, text="Irrelevant tools", font=("Arial", 12, "bold"))
    title_label.pack(pady=20)
    _add_tool_row(
        main_frame,
        label="Pwned Passwords",
        command=open_pwned_passwords_window,
        info_title="Pwned Passwords info",
        info_text="Checks if a password appears in known data breaches.",
    )
    _add_tool_row(
        main_frame,
        label="Multiply by 2",
        command=open_multiplyby2_window,
        info_title="Multiply by 2 info",
        info_text="Doubles the stored number each time you press Multiply.",
    )

    # Section title for mini games.
    title_label = ttk.Label(main_frame, text="Mini games", font=("Arial", 12, "bold"))
    title_label.pack(pady=20)
    _add_tool_row(
        main_frame,
        label="Pong",
        command=open_pong_window,
        info_title="Pong info",
        info_text=(
            "Classic arcade paddle game. Move up/down and left/right to hit "
            "the ball and score against your opponent."
        ),
    )
    _add_tool_row(
        main_frame,
        label="Knucklebones",
        command=open_knucklebone_window,
        info_title="Knucklebone info",
        info_text="a dice game, play against a bot with 3 difficulties the harder the better strategy, \n get more score by stacking dice on a single line upwards \n destroy opponent dice by placing the same number die on the same line as theirs \n all dice of this number will be destroyed, so stacking dice has its risk \n score stacks by multiplying the same number stack with depending on how many there is (goes up to 3 times of the actual amount of the dice number)",
    )
    
    _add_tool_row(
        main_frame,
        label="number guesser",
        command=open_number_guesser_window,
        info_title="Number Guesser info",
        info_text="Guess the secret number within a limited number of attempts.",
    )

    timelabel = ttk.Label(main_frame, text="")
    timelabel.pack(padx=200, pady=20)
    update_time_label(timelabel)
    return main_frame

def update_time_label(label):
    now = datetime.datetime.now()
    label.config(text=now.strftime("%d-%m-%Y %H:%M:%S"))
    label.after(100, update_time_label, label)


def _add_tool_row(parent, label, command, info_title, info_text):
    # Create a horizontal row that holds one tool button and one info button.
    row = ttk.Frame(parent)
    row.pack(pady=10, padx=20, fill=tk.X)

    # Main tool button (launches the tool).
    tool_btn = ttk.Button(row, text=label, command=command)
    tool_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Info button (shows a help message).
    info_btn = ttk.Button(
        row,
        text="ⓘ",
        width=3,
        command=lambda: messagebox.showinfo(info_title, info_text),
    )
    info_btn.pack(side=tk.LEFT, padx=(8, 0))


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

    def _cleanup_on_destroy(event):
        if event.widget is window:
            _OPEN_WINDOWS.pop(key, None)

    window.bind("<Destroy>", _cleanup_on_destroy, add="+")
    builder(window)
    return window


def open_autoclicker_window():
    """Open AutoClicker in a new window"""
    # Each tool opens in its own top-level window.
    _open_singleton_window("autoclicker", AutoClicker)

def open_number_guesser_window():
    """Open Number Guesser in a new window"""
    # Each tool opens in its own top-level window.
    _open_singleton_window("number_guesser", NumberGuesser)

def open_colourseekingcursor_window():
    """Open ColourSeekingCursor in a new window"""
    # Each tool opens in its own top-level window.
    _open_singleton_window("colourseekingcursor", ColourSeekingCursor)

def open_stopwatch_window():
    """Open Stopwatch in a new window"""
    # Each tool opens in its own top-level window.
    _open_singleton_window("stopwatch", Stopwatch)

def open_calc_window():
    """Open Calc in a new window"""
    _open_singleton_window("calc", Calc)

def open_pwned_passwords_window():
    """Open Pwned Passwords in a new window"""
    _open_singleton_window("pwned_passwords", PwnedPasswordChecker)

def open_musicfile_window():
    """Open Music File in a new window"""
    _open_singleton_window("musicfile", MusicFile)

def open_multiplyby2_window():
    """Open multiplyby2 in a new window"""
    # Each tool opens in its own top-level window.
    _open_singleton_window("multiplyby2", multiplyby2)

def open_pong_window():
    """Launch Pong as a separate process."""
    # Pong runs in a separate Python process instead of a Tk window.
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


def open_knucklebone_window():
    """Open Knucklebone in a new window"""
    _open_singleton_window("knucklebone", Knucklebone)

