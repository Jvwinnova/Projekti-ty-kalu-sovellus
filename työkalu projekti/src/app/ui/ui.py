import tkinter as tk
from tkinter import ttk
from src.app.tools.autoclicker import AutoClicker
from src.app.tools.colourseekingcursor import ColourSeekingCursor


def create_ui(root):
    """Create the main UI with tabs for different tools"""
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Title
    title_label = ttk.Label(main_frame, text="Tool Kit", font=("Arial", 16, "bold"))
    title_label.pack(pady=20)
    
    # Auto Clicker button
    autoclicker_btn = ttk.Button(main_frame, text="Auto Clicker", 
                                  command=open_autoclicker_window)
    
    autoclicker_btn.pack(pady=10, padx=20, fill=tk.X)
    
    # Colour Seeking Cursor button
    colour_btn = ttk.Button(main_frame, text="Colour Seeking Cursor", 
                             command=open_colourseekingcursor_window)
    colour_btn.pack(pady=10, padx=20, fill=tk.X)


    return main_frame


def open_autoclicker_window():
    """Open AutoClicker in a new window"""
    autoclicker_window = tk.Toplevel()
    AutoClicker(autoclicker_window)


def open_colourseekingcursor_window():
    """Open ColourSeekingCursor in a new window"""
    colourseekingcursor_window = tk.Toplevel()
    ColourSeekingCursor(colourseekingcursor_window)

