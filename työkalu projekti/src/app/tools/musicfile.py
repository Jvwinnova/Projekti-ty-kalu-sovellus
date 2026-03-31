import tkinter as tk
from tkinter import ttk

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class MusicFile:
    """Empty tool template wired to the UI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Music player")
        self.root.geometry("480x300")
        self.root.resizable(True, True)
        apply_app_icon(self.root)
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Music Player",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 8))

        ttk.Label(
            container,
            text="play mp3 files here",
            wraplength=440,
        ).pack()

        ttk.Button(container, text="Close", command=self.root.destroy).pack(pady=(16, 0))


def run():
    root = tk.Tk()
    MusicFile(root)
    root.mainloop()


if __name__ == "__main__":
    run()
