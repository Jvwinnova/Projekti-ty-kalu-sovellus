import tkinter as tk
from tkinter import ttk
import json
import os

def _get_user_config_path():
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "addandsave")
    return os.path.join(config_dir, "config.json")

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class AddAndSave:
    """Minimal window scaffold for the Add and Save tool."""
    DEFAULT_CONFIG = {"total": 0}

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Add and Save")
        self.root.geometry("420x300")
        self.root.resizable(False, False)
        apply_app_icon(self.root)
        self.config_path = _get_user_config_path()
        self.config = self.load_config()
        self.number_value = self._normalize_number(self.config.get("total", self.DEFAULT_CONFIG["total"]))

        self._build_ui()
        self._update_total_label()
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Add and Save",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 8))

        # ---- Editable Text Frame ----
        text_frame = ttk.Frame(container)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame,
            wrap="word",
            height=6,
            yscrollcommand=scrollbar.set
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.text_widget.yview)

        # Default value for quick testing.
        self.text_widget.insert("1.0", "0")

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(actions, text="Add Number", command=self.read_number_from_text).pack(side=tk.LEFT)

        ttk.Button(actions, text="Reset Number", command=self.reset).pack(side=tk.LEFT)

        self.result_var = tk.StringVar(value="")
        ttk.Label(container, textvariable=self.result_var).pack(anchor="w", pady=(0, 8))

        ttk.Button(container, text="Close", command=self.root.destroy).pack()
    def reset(self):
        self.number_value = 0
        self._update_total_label()

    def read_number_from_text(self):
        """Parse text as number and add it to the running total."""
        raw_text = self.text_widget.get("1.0", "end-1c").strip()
        if not raw_text:
            self.result_var.set("No value entered.")
            return

        try:
            # Accept both int and float input, e.g. 12 or 12.5
            parsed = float(raw_text)
        except ValueError:
            self.result_var.set(f"Invalid number: {raw_text!r}")
            return

        # Add new input to current total.
        self.number_value += parsed

        self._update_total_label()
        self.save_config()

    def _normalize_number(self, value, fallback=0):
        try:
            return float(value)
        except Exception:
            return float(fallback)

    def _update_total_label(self):
        shown_total = int(self.number_value) if float(self.number_value).is_integer() else self.number_value
        self.result_var.set(f"Total: {shown_total}")

    def load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.config["total"] = self.number_value
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def on_window_close(self):
        self.save_config()
        self.root.destroy()


def run():
    root = tk.Tk()
    AddAndSave(root)
    root.mainloop()


if __name__ == "__main__":
    run()
