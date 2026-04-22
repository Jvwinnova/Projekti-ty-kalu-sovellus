import tkinter as tk
import random
import string
import sys
from pathlib import Path

import pyperclip
from tkinter import messagebox

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


def _find_copy_icon_path() -> Path | None:
    app_dir = Path(__file__).resolve().parent
    project_root = app_dir.parent.parent.parent
    repo_root = project_root.parent
    frozen_base = Path(getattr(sys, "_MEIPASS", "")) if getattr(sys, "frozen", False) else None

    candidates = []
    if frozen_base:
        candidates.append(frozen_base / "assets" / "copy.png")

    candidates.extend((
        repo_root / "assets" / "copy.png",
        project_root / "assets" / "copy.png",
        app_dir / "assets" / "copy.png",
    ))

    for icon_path in candidates:
        if icon_path.exists():
            return icon_path

    return None


class PasswordGenerator:
    """Password generator tool."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("420x280")
        self.root.resizable(True, True)
        apply_app_icon(self.root)
        self.img = None
        copy_icon_path = _find_copy_icon_path()
        if copy_icon_path is not None:
            try:
                self.img = tk.PhotoImage(file=str(copy_icon_path))
            except tk.TclError:
                self.img = None
        self.length = 16
        self.random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=0))
        self.build_ui()
        


    def build_ui(self):
        self.length_entry = tk.Entry(self.root)
        self.length_entry.pack(pady=16)
        self.length_visual_label = tk.Label(self.root, text=f"Length: {self.length}")
        self.length_visual_label.pack(pady=16)
        self.password_label = tk.Label(self.root, text=f"password: {self.random_string}")
        self.password_label.pack(pady=5)
        if self.img is not None:
            self.copybttn = tk.Button(self.root, image=self.img, command=self._copy_to_clipboard)
        else:
            self.copybttn = tk.Button(self.root, text="Copy", command=self._copy_to_clipboard)
        self.copybttn.pack(pady=16)
        generatebttn = tk.Button(self.root, text="generate", command=self.on_generate)
        generatebttn.pack(pady=16)
        self.length_entry.bind("<KeyRelease>", self._on_entry_change)
       

    def _copy_to_clipboard(self):
        try:
            pyperclip.copy(self.random_string)
        except pyperclip.PyperclipException as exc:
            messagebox.showerror("Password Generator", f"Failed to copy password:\n{exc}")

    def _on_entry_change(self, event):
        try:
            self.length = int(self.length_entry.get())
            
            self.length_visual_label.config(text=f"Length: {self.length}")
            
        except ValueError:
            self.length = 16
            self.length_visual_label.config(text=f"cant be empty. Length: {self.length}")
            

    def on_generate(self):
        self.random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=self.length))
        self.password_label.config(text=f"password: {self.random_string}")
        
       
        
def run():
    root = tk.Tk()
    PasswordGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    run()
