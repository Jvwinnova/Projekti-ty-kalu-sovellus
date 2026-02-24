import tkinter as tk


def _is_fullscreen(window):
    return bool(window.attributes("-fullscreen"))


def toggle_fullscreen(window):
    """Toggle fullscreen mode for a given window."""
    window.attributes("-fullscreen", not _is_fullscreen(window))


def bind_fullscreen_shortcuts(window):
    """Bind fullscreen shortcuts to a window."""
    window.bind("<F11>", lambda event: toggle_fullscreen(window), add="+")


def create_menu(root):
    """Create the application menu bar"""
    
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=lambda: show_about(root))

    bind_fullscreen_shortcuts(root)
    
    return menubar


def show_about(root):
    """Show about dialog"""
    from tkinter import messagebox
    messagebox.showinfo("About", "Tool Kit\nA collection of useful and fun tools built with Python.")
