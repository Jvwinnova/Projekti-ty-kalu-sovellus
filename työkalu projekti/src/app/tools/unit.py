import tkinter as tk
from tkinter import ttk

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Unit:
    """Minimal placeholder tool that only opens a window."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Unit converter")
        self.root.geometry("360x300")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        self.container = ttk.Frame(self.root, padding=16)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.kg_to_lb = True
        ttk.Label(
            self.container,
            text="Unit converter",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 10))

        self.label = ttk.Label(
            self.container,
            text="Enter kilograms to convert to pounds",
            font=("Segoe UI", 10),
        )
        self.label.pack(pady=(0, 10))
        self.buildui()

    def buildui(self):
        self.kgentry = tk.Entry(self.container)
        self.kgentry.pack(pady=10)
        self.kgentry.bind("<KeyRelease>", self.convert_to_pounds)
        self.switch_button = ttk.Button(self.container, text="Switch Conversion", command=self.switch)
        self.switch_button.pack(pady=10)
        self.result_label = ttk.Label(self.container, text="")
        self.result_label.pack(pady=10)

    def convert_to_pounds(self, event):
        value = self.kgentry.get().strip()

        if not value:
            self.result_label.config(text="")
            return

        try:
            kg = float(value)
        except ValueError:
            self.result_label.config(text="Invalid input")
            return

        pounds = kg * 2.20462
        self.result_label.config(text=f"{kg:.2f} kg = {pounds:.2f} lbs")
    def convert_to_kilograms(self, event):
        value = self.kgentry.get().strip()

        if not value:
            self.result_label.config(text="")
            return

        try:
            lb = float(value)
        except ValueError:
            self.result_label.config(text="Invalid input")
            return

        kg = lb / 2.20462
        self.result_label.config(text=f"{lb:.2f} lbs = {kg:.2f} kg")

    def switch(self):
        if self.kg_to_lb:
            self.kg_to_lb = False
            self.label.config(text="Enter pounds to convert to kilograms")
            self.kgentry.bind("<KeyRelease>", self.convert_to_kilograms)
            self.convert_to_kilograms(None)  # Update result immediately when switching
        else:
            self.kg_to_lb = True
            self.label.config(text="Enter kilograms to convert to pounds")
            self.kgentry.bind("<KeyRelease>", self.convert_to_pounds)
            self.convert_to_pounds(None)  # Update result immediately when switching back
           

      


def run():
    root = tk.Tk()
    Unit(root)
    root.mainloop()


if __name__ == "__main__":
    run()