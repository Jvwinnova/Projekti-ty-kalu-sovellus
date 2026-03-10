import tkinter as tk
from tkinter import ttk
import json
import os

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


def _get_user_config_path():
    # Store config in a user-writable roaming location.
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "ToolKit")
    return os.path.join(config_dir, "config.json")


class multiplyby2:
    """Basic window scaffold for a new tool."""

    DEFAULT_CONFIG = {
        "Multiply by 2": {
            "number": 1
        }
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Multiply by 2")
        self.root.geometry("520x360")
        self.root.resizable(True, True)
        apply_app_icon(self.root)

        # Load persisted tool state.
        self.config_path = _get_user_config_path()
        self.config = self.load_config()
        self.number = self._normalize_number(
            self.config["Multiply by 2"]["number"],
            fallback=self.DEFAULT_CONFIG["Multiply by 2"]["number"],
        )
        self.status_var = tk.StringVar(value=f"Number: {self.number}")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)
        container.bind("<Configure>", self._on_container_configure)

        ttk.Label(
            container,
            text="2 times",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            container,
            text="Multiply by 2",
            wraplength=480,
        ).pack(pady=(0, 12))

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 10))
        # call functions through buttons
        ttk.Button(actions, text="Multiply", command=self.on_run_action).pack(side=tk.LEFT)
        ttk.Button(actions, text="Reset", command=self.on_reset).pack(side=tk.LEFT, padx=(8, 0))

        self.status_label = ttk.Label(
            container,
            textvariable=self.status_var,
            wraplength=480,
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(0, 160), fill=tk.X)

        ttk.Button(container, text="Close", command=self.root.destroy).pack()
    # multiplies current number by 2 and sets status label to show the current number.
    def on_run_action(self):
        self.number *= 2
        self.status_var.set(f"Number: {self.number}")
        self._persist_number()
    #resets the number to 1 and updates the status label
    def on_reset(self):
        self.number = 1
        self.status_var.set(f"Number: {self.number}")
        self._persist_number()

    def _normalize_number(self, value, fallback=1):
        # Keep state resilient to invalid config values.
        try:
            return int(value)
        except Exception:
            try:
                return int(float(value))
            except Exception:
                return int(fallback)

    def _persist_number(self):
        # Update and store the current tool state.
        self.config["Multiply by 2"]["number"] = self.number
        self.save_config()

    def load_config(self):
        # Merge loaded config with defaults to keep missing keys safe.
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if not isinstance(loaded, dict):
                    loaded = {}
                merged = self.DEFAULT_CONFIG.copy()
                merged.update(loaded)
                section = self.DEFAULT_CONFIG["Multiply by 2"].copy()
                section.update(merged.get("Multiply by 2", {}))
                merged["Multiply by 2"] = section
                return merged
            except Exception:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        # Persist config without blocking the UI on errors.
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def on_window_close(self):
        # Save before closing so state is preserved.
        self._persist_number()
        self.root.destroy()

    def _on_container_configure(self, event):
        # Ensure long numbers wrap instead of clipping offscreen.
        wrap = max(event.width - 32, 200)
        self.status_label.configure(wraplength=wrap)


def run():
    root = tk.Tk()
    multiplyby2(root)
    root.mainloop()


if __name__ == "__main__":
    run()
