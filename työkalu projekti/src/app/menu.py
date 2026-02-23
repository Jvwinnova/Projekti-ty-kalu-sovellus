import tkinter as tk
from tkinter import ttk


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
    
    return menubar


def show_about(root):
    """Show about dialog"""
    from tkinter import messagebox
    messagebox.showinfo("About", "Tool Kit\nA collection of useful and fun tools built with Python.")
