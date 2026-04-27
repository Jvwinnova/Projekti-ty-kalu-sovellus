"""Auto clicker with persisted settings and a global toggle hotkey."""

# Import GUI library
import tkinter as tk
from tkinter import ttk, messagebox

# Import threading so the clicker can run without freezing the GUI
import threading

# Used for timing between clicks
import time

# Library that performs mouse clicks
import pyautogui

# Used to save/load settings
import json
import os

# Used to detect global hotkeys
import keyboard

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


# Remove built-in delay between pyautogui actions
pyautogui.PAUSE = 0

# Move mouse to top-left corner to trigger failsafe stop
pyautogui.FAILSAFE = True


def _get_user_config_path():
    """Return the shared config file path used by ToolKit tools."""
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "ToolKit")
    return os.path.join(config_dir, "config.json")


class AutoClicker:
    """Repeatedly click the mouse until stopped by UI or hotkey."""

    # Default config values used for the first time
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
        self.root.geometry("500x400")
        #applies the app icon to the window
        apply_app_icon(self.root)
        #calls a function to set up fullscreen toggle on F11
        self._setup_fullscreen_controls()
         
        

        # Tracks whether auto-clicking is active
        self.is_running = False

        # Thread that runs the clicking loop
        self.thread = None

        # Event used to safely stop the clicking thread
        self.stop_event = threading.Event()
        self.hotkey_binding = None
        self.hotkey_hook = None
        self.hotkey_is_down = False
        self.is_recording_hotkey = False

        # Path to config file in a user-writable location
        self.config_path = _get_user_config_path()

        # Load settings from file
        self.config = self.load_config()
        autoclicker = self.config["autoclicker"]

        # Apply loaded settings
        self.current_hotkey = autoclicker["hotkey"]
        self.interval_var = tk.DoubleVar(value=autoclicker["click_interval"])
        self.button_var = tk.StringVar(value=autoclicker["mouse_button"])

        # Automatically save settings when changed
        self.interval_var.trace_add("write", self.on_settings_change)
        self.button_var.trace_add("write", self.on_settings_change)

        

        # ---------------- UI ---------------- #
        ttk.Label(self.root, text="Auto Clicker",
                  font=("Segoe UI", 13, "bold")).pack(pady=10)
        ttk.Label(self.root, text="Automatically click with the cursor").pack(pady=5)

        ttk.Label(root, text="Click Delay (seconds):").pack(pady=5)
        ttk.Entry(root, textvariable=self.interval_var).pack()

        ttk.Label(root, text="Mouse Button:").pack(pady=5)
        ttk.Combobox(
            root,
            textvariable=self.button_var,
            values=["left", "right", "middle"],
            state="readonly"
        ).pack()

        # Status label shows if clicker is running
        self.status_label = ttk.Label(root, text="Status: Stopped", foreground="red")
        self.status_label.pack(pady=10)

        ttk.Separator(root, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(root, text="Hotkey Settings", font=("Arial", 10, "bold")).pack(pady=5)
        ttk.Label(root, text="Current Hotkey:").pack()

        hotkey_frame = ttk.Frame(root)
        hotkey_frame.pack(pady=10, padx=20, fill=tk.X)

        # Displays current hotkey (read-only)
        self.hotkey_display = ttk.Entry(hotkey_frame, state="readonly")
        self.hotkey_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.update_hotkey_display()

        # Button to record new hotkey
        ttk.Button(hotkey_frame, text="Bind a shortcut key", command=self.record_hotkey).pack(side=tk.LEFT, padx=5)

        # Button to reset hotkey to default
        ttk.Button(hotkey_frame, text="Reset to default", command=self.reset_hotkey).pack(side=tk.LEFT, padx=5)

       
        


        # Small label that shows "Press a key..."
        self.record_label = ttk.Label(root, text="", foreground="blue")
        self.record_label.pack(pady=5)

        # When window is closed, call cleanup function
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Bind the hotkey immediately
        self.bind_hotkey()

    # ---------------- Window Controls ---------------- #
    def _setup_fullscreen_controls(self):
        self.root.bind("<F11>", lambda event: self.toggle_fullscreen(), add="+")

    def toggle_fullscreen(self):
        self.root.attributes("-fullscreen", not bool(self.root.attributes("-fullscreen")))

    # ---------------- Config ---------------- #

    # Load config file if it exists
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    loaded = json.load(f)
                    if not isinstance(loaded, dict):
                        loaded = {}
                    merged = self.DEFAULT_CONFIG.copy()
                    merged.update(loaded)
                    merged_section = self.DEFAULT_CONFIG["autoclicker"].copy()
                    merged_section.update(merged.get("autoclicker", {}))
                    merged["autoclicker"] = merged_section
                    return merged
            except Exception:
                pass

        # If loading fails, return default settings
        return self.DEFAULT_CONFIG.copy()

    # Save current settings to file
    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Called automatically when interval or mouse button changes
    def on_settings_change(self, *args):
        self.config["autoclicker"]["click_interval"] = self.interval_var.get()
        self.config["autoclicker"]["mouse_button"] = self.button_var.get()
        self.save_config()

    # ---------------- Clicking Logic ---------------- #

    # Start or stop clicking
    def toggle_clicking(self):
        self.is_running = not self.is_running

        if self.is_running:
            # Start clicking
            self.stop_event.clear()
            self.status_label.config(text="Status: Running", foreground="green")

            # Run click loop in background thread
            self.thread = threading.Thread(target=self.click_loop, daemon=True)
            self.thread.start()
        else:
            # Stop clicking
            self.stop_event.set()
            self.status_label.config(text="Status: Stopped", foreground="red")

    # The loop that repeatedly clicks
    def click_loop(self):
        while self.is_running:

            # Perform click
            pyautogui.click(button=self.button_var.get())

            # Get interval safely
            try:
                interval = float(self.interval_var.get())
            except (tk.TclError, ValueError):
                interval = 0.01

            # Prevent extremely small or negative values
            interval = max(0.001, interval)

            # Wait for interval, but allow early stop
            if self.stop_event.wait(timeout=interval):
                break

    # ---------------- Hotkeys ---------------- #
    
    def _normalize_hotkey(self, hotkey):
        """Store hotkeys in a consistent lowercase form."""
        return str(hotkey).strip().lower()

    def _is_single_key_hotkey(self, hotkey):
        """Detect whether the binding is a plain key or a combo expression."""
        return "+" not in hotkey and "," not in hotkey

    def _safe_after(self, callback):
        """Schedule UI work only if the Tk window still exists."""
        try:
            self.root.after(0, callback)
            return True
        except tk.TclError:
            return False

    def _request_toggle(self):
        if self.is_recording_hotkey:
            return
        self._safe_after(self.toggle_clicking)

    def _handle_single_key_hotkey_event(self, event):
        if self.is_recording_hotkey:
            return
        if event.event_type == "down":
            if self.hotkey_is_down:
                return
            self.hotkey_is_down = True
            self._request_toggle()
        elif event.event_type == "up":
            self.hotkey_is_down = False

    # Remove only this tool's hotkey binding
    def safe_remove_hotkey_binding(self):
        if not self.hotkey_binding:
            return
        try:
            keyboard.remove_hotkey(self.hotkey_binding)
        except Exception:
            try:
                keyboard.unhook(self.hotkey_binding)
            except Exception:
                pass
        finally:
            self.hotkey_binding = None
            self.hotkey_is_down = False

    # Bind the selected hotkey to toggle clicking
    def bind_hotkey(self):
        self.safe_remove_hotkey_binding()
        hotkey = self._normalize_hotkey(self.current_hotkey)
        self.current_hotkey = hotkey
        try:
            if self._is_single_key_hotkey(hotkey):
                self.hotkey_binding = keyboard.hook_key(hotkey, self._handle_single_key_hotkey_event)
            else:
                self.hotkey_binding = keyboard.add_hotkey(hotkey, self._request_toggle)
        except Exception as e:
            self.hotkey_binding = None
            self.hotkey_is_down = False
            self.status_label.config(text=f"Status: Hotkey error ({e})", foreground="red")

    # Record a new hotkey from user input
    def record_hotkey(self):
        self.is_recording_hotkey = True
        self.safe_remove_hotkey_binding()
        self.record_label.config(text="Press a key...", foreground="blue")
        if self.hotkey_hook:
            keyboard.unhook(self.hotkey_hook)
            self.hotkey_hook = None

        def on_key(event):
            if event.event_type == "down":
                self.current_hotkey = event.name
                self.update_hotkey_display()
                self.bind_hotkey()
                self.is_recording_hotkey = False

                # Save new hotkey
                self.config["autoclicker"]["hotkey"] = self.current_hotkey
                self.save_config()

                self.record_label.config(text="")
                if self.hotkey_hook:
                    keyboard.unhook(self.hotkey_hook)
                    self.hotkey_hook = None

        try:
            self.hotkey_hook = keyboard.hook(on_key)
        except Exception as e:
            self.is_recording_hotkey = False
            self.bind_hotkey()
            self.hotkey_hook = None
            self.record_label.config(text="")
            self.status_label.config(text=f"Status: Hotkey record error ({e})", foreground="red")

    # Reset hotkey back to default
    def reset_hotkey(self):
        self.current_hotkey = self.DEFAULT_CONFIG["autoclicker"]["hotkey"]
        self.update_hotkey_display()
        self.bind_hotkey()

        self.config["autoclicker"]["hotkey"] = self.current_hotkey
        self.save_config()

    # Update the read-only hotkey display box
    def update_hotkey_display(self):
        self.hotkey_display.config(state="normal")
        self.hotkey_display.delete(0, tk.END)
        self.hotkey_display.insert(0, self.current_hotkey)
        self.hotkey_display.config(state="readonly")

    # ---------------- Closing App ---------------- #

    # Cleanly stop everything before closing window
    def on_window_close(self):
        self.is_running = False
        self.stop_event.set()
        if self.hotkey_hook:
            keyboard.unhook(self.hotkey_hook)
            self.hotkey_hook = None
        self.safe_remove_hotkey_binding()
        self.root.destroy()


# Start the program
if __name__ == "__main__":
    root = tk.Tk()
    AutoClicker(root)
    root.mainloop()
