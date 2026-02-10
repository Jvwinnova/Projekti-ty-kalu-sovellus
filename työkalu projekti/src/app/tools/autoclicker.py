import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import json
import os
import keyboard


class AutoClicker:
    DEFAULT_CONFIG = {
        "autoclicker": {
            "hotkey": "f3",
            "click_interval": 0.01,
            "mouse_button": "left"
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("350x380")

        self.is_running = False
        self.thread = None
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")

        # Load config
        self.config = self.load_config()
        autoclicker = self.config["autoclicker"]

        # Apply config instantly
        self.current_hotkey = autoclicker["hotkey"]
        self.interval_var = tk.DoubleVar(value=autoclicker["click_interval"])
        self.button_var = tk.StringVar(value=autoclicker["mouse_button"])

        # Auto-save on change
        self.interval_var.trace_add("write", self.on_settings_change)
        self.button_var.trace_add("write", self.on_settings_change)

        # UI
        ttk.Label(root, text="Click Interval (seconds):").pack(pady=5)
        ttk.Entry(root, textvariable=self.interval_var).pack()

        ttk.Label(root, text="Mouse Button:").pack(pady=5)
        ttk.Combobox(
            root,
            textvariable=self.button_var,
            values=["left", "right", "middle"],
            state="readonly"
        ).pack()

        self.status_label = ttk.Label(root, text="Status: Stopped", foreground="red")
        self.status_label.pack(pady=10)

        ttk.Separator(root, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(root, text="Hotkey Settings", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Label(root, text="Current Hotkey:").pack()

        hotkey_frame = ttk.Frame(root)
        hotkey_frame.pack(pady=10, padx=20, fill=tk.X)

        self.hotkey_display = ttk.Entry(hotkey_frame, state="readonly")
        self.hotkey_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.hotkey_display.insert(0, self.current_hotkey)

        ttk.Button(hotkey_frame, text="Record", command=self.record_hotkey).pack(side=tk.LEFT, padx=5)
        ttk.Button(hotkey_frame, text="Reset", command=self.reset_hotkey).pack(side=tk.LEFT, padx=5)

        self.record_label = ttk.Label(root, text="", foreground="blue")
        self.record_label.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.bind_hotkey()

    # ---------------- Config ---------------- #
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_settings_change(self, *args):
        self.config["autoclicker"]["click_interval"] = self.interval_var.get()
        self.config["autoclicker"]["mouse_button"] = self.button_var.get()
        self.save_config()

    # ---------------- Clicking ---------------- #
    def toggle_clicking(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.status_label.config(text="Status: Running", foreground="green")
            self.thread = threading.Thread(target=self.click_loop, daemon=True)
            self.thread.start()
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")

    def click_loop(self):
        while self.is_running:
            pyautogui.click(button=self.button_var.get())
            time.sleep(self.interval_var.get())

    # ---------------- Hotkeys ---------------- #
    def safe_unhook_all_hotkeys(self):
        try:
            keyboard.unhook_all_hotkeys()
        except AttributeError:
            pass

    def bind_hotkey(self):
        self.safe_unhook_all_hotkeys()
        keyboard.add_hotkey(self.current_hotkey, self.toggle_clicking)

    def record_hotkey(self):
        self.record_label.config(text="Press a key...", foreground="blue")

        def on_key(event):
            if event.event_type == "down":
                self.current_hotkey = event.name
                self.update_hotkey_display()
                self.bind_hotkey()

                self.config["autoclicker"]["hotkey"] = self.current_hotkey
                self.save_config()

                self.record_label.config(text="")
                keyboard.unhook(on_key)

        keyboard.hook(on_key)

    def reset_hotkey(self):
        self.current_hotkey = self.DEFAULT_CONFIG["autoclicker"]["hotkey"]
        self.update_hotkey_display()
        self.bind_hotkey()

        self.config["autoclicker"]["hotkey"] = self.current_hotkey
        self.save_config()

    def update_hotkey_display(self):
        self.hotkey_display.config(state="normal")
        self.hotkey_display.delete(0, tk.END)
        self.hotkey_display.insert(0, self.current_hotkey)
        self.hotkey_display.config(state="readonly")

    # ---------------- Close ---------------- #
    def on_window_close(self):
        self.is_running = False
        self.safe_unhook_all_hotkeys()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    AutoClicker(root)
    root.mainloop()
