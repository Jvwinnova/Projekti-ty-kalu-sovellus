import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from src.app.tools.autoclicker import AutoClicker
from src.app.tools.colourseekingcursor import ColourSeekingCursor
from src.app.tools.Multiplyby2 import multiplyby2
from src.app.tools.stopwatch import Stopwatch


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
        info_title="Auto Clicker",
        info_text="Automatically clicks at a configurable speed.",
    )

    _add_tool_row(
        main_frame,
        label="Colour Seeking Cursor",
        command=open_colourseekingcursor_window,
        info_title="Colour Seeking Cursor",
        info_text="Moves the cursor toward a target color on screen.",
    )

    _add_tool_row(
        main_frame,
        label="Stopwatch",
        command=open_stopwatch_window,
        info_title="Stop watch",
        info_text="Simple stopwatch with start, stop, and reset.",
    )

    # Section title for tools that are less important.
    title_label = ttk.Label(main_frame, text="Irrelevant tools", font=("Arial", 12, "bold"))
    title_label.pack(pady=20)

    _add_tool_row(
        main_frame,
        label="Multiply by 2",
        command=open_multiplyby2_window,
        info_title="Multiply by 2",
        info_text="Doubles the stored number each time you press Multiply.",
    )

    # Section title for mini games.
    title_label = ttk.Label(main_frame, text="Mini games", font=("Arial", 12, "bold"))
    title_label.pack(pady=20)
    _add_tool_row(
        main_frame,
        label="Pong",
        command=open_pong_window,
        info_title="Pong",
        info_text=(
            "Classic arcade paddle game. Move up/down and left/right to hit "
            "the ball and score against your opponent."
        ),
    )

    return main_frame


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


def open_autoclicker_window():
    """Open AutoClicker in a new window"""
    # Each tool opens in its own top-level window.
    autoclicker_window = tk.Toplevel()
    AutoClicker(autoclicker_window)


def open_colourseekingcursor_window():
    """Open ColourSeekingCursor in a new window"""
    # Each tool opens in its own top-level window.
    colourseekingcursor_window = tk.Toplevel()
    ColourSeekingCursor(colourseekingcursor_window)

def open_stopwatch_window():
    """Open Stopwatch in a new window"""
    # Each tool opens in its own top-level window.
    stopwatch_window = tk.Toplevel()
    Stopwatch(stopwatch_window)

def open_multiplyby2_window():
    """Open multiplyby2 in a new window"""
    # Each tool opens in its own top-level window.
    multiplyby2_window = tk.Toplevel()
    multiplyby2(multiplyby2_window)

def open_pong_window():
    """Launch Pong as a separate process."""
    # Pong runs in a separate Python process instead of a Tk window.
    try:
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--pong"]
        else:
            cmd = [sys.executable, "-m", "src.app.tools.pong"]
        subprocess.Popen(cmd, cwd=project_root)
    except Exception as e:
        messagebox.showerror("Pong", f"Failed to launch Pong:\n{e}")

