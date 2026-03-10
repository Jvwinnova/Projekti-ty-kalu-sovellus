import tkinter as tk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.app.menu import create_menu
from src.app.ui.ui import create_ui
from src.app.window_icon import apply_app_icon


def main():
    """Initialize and run the application"""
    
    root = tk.Tk()
    root.title("Tool Kit")
    root.geometry("400x600")
    apply_app_icon(root)
    
    # Create menu bar
    create_menu(root)
    
    # Create UI with tabs
    create_ui(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()
