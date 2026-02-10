import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import math
import time
import keyboard
import json
import threading
import os


class ColourSeekingCursor:
    """A GUI app that moves the mouse toward the nearest cluster of a chosen color,
    with color tolerance and reliable hotkey handling."""

    # ------------------------ Constants ------------------------
    CONFIG_SECTION = "colourseekingcursor"
    SEARCH_RADIUS = 100      # How far around the cursor to look for the color
    COLOR_THRESHOLD = 100    # Maximum distance in RGB space to consider a pixel "matching"
    SAMPLE_STEP = 5          # Step size when scanning pixels (higher = faster, less accurate)
    LOOP_DELAY = 0.1         # Delay between each seek iteration

    # Default settings
    DEFAULT_CONFIG = {
        "hotkey": "f3",       # Key to start seeking
        "speed": 5.0,         # How fast the mouse moves toward the color
        "target_r": 255,      # Default target color: red
        "target_g": 0,
        "target_b": 0,
        "tolerance": 100      # Max color difference allowed
    }

    # ------------------------ Initialization ------------------------
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Colour Seeking Cursor")
        self.root.geometry("440x550")
        self.root.resizable(False, False)

        # Flags for running state
        self.is_running = False
        self.worker_thread = None

        # Path to config file (one folder above this script)
        self.config_path = os.path.join(
            os.path.dirname(__file__), "..", "config.json"
        )

        # Load config or use defaults
        self.config = self.load_config()
        self.settings = self.config.setdefault(
            self.CONFIG_SECTION, self.DEFAULT_CONFIG.copy()
        )
        self.current_hotkey = self.settings["hotkey"]

        # Build the GUI
        self._build_ui()
        self.bind_hotkey()

        # Handle closing window
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    # ------------------------ UI Construction ------------------------
    def _build_ui(self):
        ttk.Label(self.root, text="Colour Seeking Cursor",
                  font=("Segoe UI", 13, "bold")).pack(pady=10)
        ttk.Label(self.root, text="Moves the mouse toward a selected screen color").pack(pady=5)

        self._build_color_controls()
        self._build_speed_controls()
        self._build_tolerance_control()
        self._build_buttons()
        self._build_status()
        self._build_hotkey_section()

        ttk.Button(
            self.root,
            text="Save Settings",
            command=self.save_settings,
        ).pack(pady=10, padx=20, fill=tk.X)

    def _build_color_controls(self):
        ttk.Label(self.root, text="Target Color (RGB)").pack(pady=5)
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=10, fill=tk.X)

        self.r_var = tk.IntVar(value=self.settings["target_r"])
        self.g_var = tk.IntVar(value=self.settings["target_g"])
        self.b_var = tk.IntVar(value=self.settings["target_b"])

        for label, var in (("R", self.r_var), ("G", self.g_var), ("B", self.b_var)):
            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT, padx=5)
            ttk.Spinbox(frame, from_=0, to=255, width=5, textvariable=var).pack(side=tk.LEFT, padx=5)

    def _build_speed_controls(self):
        ttk.Label(self.root, text="Movement Speed").pack(pady=5)
        self.speed_var = tk.DoubleVar(value=self.settings["speed"])
        ttk.Scale(
            self.root, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.speed_var
        ).pack(padx=20, fill=tk.X)

    def _build_tolerance_control(self):
        ttk.Label(self.root, text="Color Tolerance (Max Difference)").pack(pady=5)
        self.tolerance_var = tk.DoubleVar(value=self.settings.get("tolerance", 100))
        ttk.Scale(
            self.root, from_=10, to=255, orient=tk.HORIZONTAL, variable=self.tolerance_var
        ).pack(padx=20, fill=tk.X)

    def _build_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=15, padx=20, fill=tk.X)

        ttk.Button(frame, text="Start", command=self.start_seeking).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(frame, text="Stop", command=self.stop_seeking).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _build_status(self):
        self.status_label = ttk.Label(
            self.root, text="Status: Stopped", foreground="red"
        )
        self.status_label.pack(pady=10)

    def _build_hotkey_section(self):
        ttk.Separator(self.root).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(
            self.root, text="Hotkey Settings", font=("Segoe UI", 10, "bold")
        ).pack(pady=5)

        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=5, fill=tk.X)

        self.hotkey_display = ttk.Entry(frame, state="readonly")
        self.hotkey_display.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.update_hotkey_display()

        ttk.Button(frame, text="Record", command=self.record_hotkey).pack(side=tk.LEFT)
        ttk.Button(frame, text="Reset", command=self.reset_hotkey).pack(side=tk.LEFT)

        self.record_label = ttk.Label(self.root, foreground="blue")
        self.record_label.pack(pady=5)

    # ------------------------ Configuration ------------------------
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
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config:\n{e}")

    # ------------------------ Seeking Logic ------------------------
    def start_seeking(self):
        if self.is_running:
            return  # Already running
        self.is_running = True
        self.status_label.config(text="Status: Seeking", foreground="green")
        self.worker_thread = threading.Thread(
            target=self.seeking_loop, daemon=True
        )
        self.worker_thread.start()

    def stop_seeking(self):
        self.is_running = False
        self.status_label.config(text="Status: Stopped", foreground="red")

    def seeking_loop(self):
        while self.is_running:
            try:
                self._seek_step()
                time.sleep(self.LOOP_DELAY)
            except Exception:
                time.sleep(0.2)

    def _seek_step(self):
        """Seek the closest cluster within the color tolerance."""
        target = (self.r_var.get(), self.g_var.get(), self.b_var.get())
        speed = self.speed_var.get()
        tolerance = self.tolerance_var.get()

        cx, cy = pyautogui.position()
        sw, sh = pyautogui.size()

        best_cluster = None
        best_distance = float("inf")
        matching_pixels = []

        # Scan pixels in the search area
        for y in range(max(0, cy - self.SEARCH_RADIUS), min(sh, cy + self.SEARCH_RADIUS), self.SAMPLE_STEP):
            for x in range(max(0, cx - self.SEARCH_RADIUS), min(sw, cx + self.SEARCH_RADIUS), self.SAMPLE_STEP):
                r, g, b = pyautogui.pixel(x, y)
                color_diff = math.dist((r, g, b), target)
                if color_diff <= tolerance:
                    matching_pixels.append((x, y))

        if matching_pixels:
            # Compute cluster center
            avg_x = sum(p[0] for p in matching_pixels) / len(matching_pixels)
            avg_y = sum(p[1] for p in matching_pixels) / len(matching_pixels)

            # Distance from current cursor
            dx, dy = avg_x - cx, avg_y - cy
            distance = math.hypot(dx, dy)

            if distance < best_distance:
                best_distance = distance
                best_cluster = (avg_x, avg_y)

            if best_cluster:
                dx, dy = best_cluster[0] - cx, best_cluster[1] - cy
                length = math.hypot(dx, dy)
                if length:
                    pyautogui.moveRel(dx / length * speed, dy / length * speed, duration=0.05)

    # ------------------------ Hotkeys ------------------------
    def bind_hotkey(self):
        """Bind hotkey to start seeking safely"""
        keyboard.unhook_all_hotkeys()
        keyboard.add_hotkey(self.current_hotkey, self.start_seeking)

    def record_hotkey(self):
        """Wait for a key press and record it as hotkey"""
        self.record_label.config(text="Press desired hotkey...")
        self.root.after(100, self._wait_for_hotkey)

    def _wait_for_hotkey(self):
        """Blocking wait for the next key press"""
        event = keyboard.read_event(suppress=True)  # Waits until a key is pressed
        if event.event_type == "down":
            self.current_hotkey = event.name
            self.update_hotkey_display()
            self.bind_hotkey()
        self.record_label.config(text="")

    def reset_hotkey(self):
        self.current_hotkey = self.DEFAULT_CONFIG["hotkey"]
        self.update_hotkey_display()
        self.bind_hotkey()

    def update_hotkey_display(self):
        self.hotkey_display.config(state="normal")
        self.hotkey_display.delete(0, tk.END)
        self.hotkey_display.insert(0, self.current_hotkey)
        self.hotkey_display.config(state="readonly")

    # ------------------------ Misc ------------------------
    def save_settings(self):
        self.settings.update(
            hotkey=self.current_hotkey,
            speed=self.speed_var.get(),
            target_r=self.r_var.get(),
            target_g=self.g_var.get(),
            target_b=self.b_var.get(),
            tolerance=self.tolerance_var.get()
        )
        self.save_config()
        messagebox.showinfo("Success", "Settings saved successfully.")

    def on_window_close(self):
        self.stop_seeking()
        keyboard.unhook_all_hotkeys()
        self.save_settings()
        self.root.destroy()


# ------------------------ Run the app ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ColourSeekingCursor(root)
    root.mainloop()
