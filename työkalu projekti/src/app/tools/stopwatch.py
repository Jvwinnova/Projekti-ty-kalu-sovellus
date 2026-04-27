"""Stopwatch with persisted elapsed time and a configurable hotkey."""

import json
import math
import os
import time
import tkinter as tk
import keyboard
from tkinter import messagebox

def _get_user_config_path():
    """Return per-user config file path for this app."""
    # Store config in AppData so settings persist between app launches.
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "ToolKit")
    return os.path.join(config_dir, "config.json")

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Stopwatch:
    """Start, stop, reset, and persist a stopwatch session."""
    CONFIG_SECTION = "stopwatch"
    def __init__(self, root: tk.Tk):
        self._get_user_config_path = _get_user_config_path
        self.root = root
        self.root.title("Stopwatch")
        self.root.geometry("360x220")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        default_config = {
            "elapsed_time": 0.0,
            "shortcut": "f3",
        }
        self.elapsed_time = default_config["elapsed_time"]
        self.shortcut = default_config["shortcut"]
        self.running = False
        self._start_time = 0.0
        self._tick_job = None
        self._hotkey_id = None
        self._binding_hook = None
        self._binding_active = False

        self.config_path = self._get_user_config_path()
        self._load_config()
        self._build_ui()
        self._bind_shortcut()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def _build_ui(self):
        """Initialize state, load settings, build UI, and bind hotkeys."""
        self.time_label = tk.Label(
            self.root,
            text=self._format_time(self.elapsed_time),
            font=("Consolas", 20, "bold"),
        )
        self.time_label.pack(pady=20)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Start", command=self.start).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Stop", command=self.stop).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Bind hotkey", command=self.bind_shortcut).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="ⓘ", command=lambda: tk.messagebox.showinfo("Stopwatch Info", "00:00:00:00\n\n stop watch uses: hours, minutes, seconds, hundredths. ")).pack(side=tk.LEFT, padx=5, pady=5)


        self.shortcut_var = tk.StringVar(value=f"hotkey: {self.shortcut}")
        self.shortcut_label = tk.Label(self.root, textvariable=self.shortcut_var, font=("Arial", 10))
        self.shortcut_label.pack(pady=(0, 10))

    def bind_shortcut(self):
        """Bind a new shortcut key for starting/stopping the stopwatch."""
        if self._binding_active:
            return
        self._binding_active = True
        self.shortcut_var.set("Press desired hotkey...")

        def on_key_press(event):
            if not self._binding_active:
                return
            key = event.name
            self.shortcut_var.set(f"hotkey: {key}")
            
            self.shortcut = key
            self._binding_active = False
            self._clear_binding_hook()
            self._save_config()
            self._bind_shortcut()

        self._binding_hook = keyboard.hook(on_key_press)
    
    
    def on_closing(self):
        """Handle window closing event."""
        if self.running:
            self.elapsed_time = time.perf_counter() - self._start_time
        self._cancel_tick()
        self._clear_binding_hook()
        self._unbind_shortcut()
        self._save_config()
        self.root.destroy()

    def _format_time(self, seconds):
        """Format elapsed time in seconds to MM:SS:MS format."""
        total_seconds = float(seconds)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        whole_seconds = int(total_seconds % 60)
        hundredths = int((total_seconds - int(total_seconds)) * 100)
        return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}:{hundredths:02d}"

    def _load_config(self):
        try:
            if not os.path.exists(self.config_path):
                return
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            section = data.get(self.CONFIG_SECTION, {})
            elapsed = float(section.get("elapsed_time", self.elapsed_time))
            if not math.isfinite(elapsed) or elapsed < 0:
                elapsed = 0.0
            self.elapsed_time = elapsed
            self.shortcut = str(section.get("shortcut", self.shortcut))
        except Exception:
            pass

    def _save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            data = {}
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except Exception:
                    data = {}
            data[self.CONFIG_SECTION] = {
                "elapsed_time": self.elapsed_time,
                "shortcut": self.shortcut,
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


    def start(self):
        """Start the stopwatch."""
        if not self.running:
            self.running = True
            self._start_time = time.perf_counter() - self.elapsed_time
            self._schedule_tick()
    
    def stop(self):
        """Stop the stopwatch."""
        if not self.running:
            return
        self.running = False
        self.elapsed_time = time.perf_counter() - self._start_time
        self._cancel_tick()
        self._update_display()
        self._save_config()
        
    
    def reset(self):
        """Reset the stopwatch to zero."""
        self.running = False
        self.elapsed_time = 0.0
        self._cancel_tick()
        self._update_display()
        self._save_config()
       
    
    def _schedule_tick(self):
        """Queue the next UI refresh while the stopwatch is running."""
        self._cancel_tick()
        self._tick_job = self.root.after(30, self._tick)

    def _cancel_tick(self):
        """Cancel any pending scheduled refresh callback."""
        if self._tick_job is not None:
            self.root.after_cancel(self._tick_job)
            self._tick_job = None

    def _tick(self):
        """Refresh elapsed time and requeue another update."""
        if not self.running:
            return
        self.elapsed_time = time.perf_counter() - self._start_time
        self._update_display()
        self._schedule_tick()

    def _update_display(self):
        """Refresh the visible time label from the current elapsed value."""
        self.time_label.config(text=self._format_time(self.elapsed_time))

    def _toggle_running(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def _bind_shortcut(self):
        self._unbind_shortcut()
        try:
            self._hotkey_id = keyboard.add_hotkey(self.shortcut, self._toggle_running)
            if hasattr(self, "shortcut_var"):
                self.shortcut_var.set(f"hotkey: {self.shortcut}")
                self.stop()
               
        except Exception:
            if hasattr(self, "shortcut_var"):
                self.shortcut_var.set(f"hotkey: {self.shortcut} (unavailable)")

    def _unbind_shortcut(self):
        if self._hotkey_id is not None:
            try:
                keyboard.remove_hotkey(self._hotkey_id)
            except Exception:
                pass
            self._hotkey_id = None

    def _clear_binding_hook(self):
        if self._binding_hook is not None:
            try:
                keyboard.unhook(self._binding_hook)
            except Exception:
                pass
            self._binding_hook = None


def run():
    """Launch the Stopwatch tool."""
    root = tk.Tk()
    Stopwatch(root)
    root.mainloop()


if __name__ == "__main__":
    run()
