"""Move the cursor toward nearby clusters of matching on-screen colors."""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import pyautogui
import math
import time
import keyboard
import json
import threading
import os
import ctypes
from ctypes import wintypes
from PIL import ImageGrab
try:
    from tkcolorpicker import askcolor as wheel_askcolor
except Exception:
    wheel_askcolor = None

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        """Fallback when icon helper is unavailable; do nothing."""
        return


def _get_user_config_path():
    """Return per-user config file path for this app."""
    # Store config in AppData so settings persist between app launches.
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "ToolKit")
    return os.path.join(config_dir, "config.json")


class ColourSeekingCursor:
    """An app that jumps the mouse to the center of a nearby matching color cluster."""

    CONFIG_SECTION = "colourseekingcursor"
    SAMPLE_STEP = 5          # Step size when scanning pixels (higher = faster, less accurate)
    LOOP_DELAY = 0.0001         # Delay between each seek iteration
    TOGGLE_DEBOUNCE = 0.2    # Ignore repeated hotkey events fired too quickly
    STOP_JOIN_TIMEOUT = 0.5
    Strength = " "
    DEFAULT_CONFIG = {
        "hotkey": "f3",
        "colors": [
            {"r": 255, "g": 0, "b": 0}
        ],
        "tolerance": 100,
        "min_cluster_size": 3
    }

    def __init__(self, root: tk.Tk):
        """Initialize state, load settings, build UI, and bind hotkeys."""
        self.root = root
        self.root.title("Colour Seeking Cursor")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        # Make cursor warps immediate with no implicit PyAutoGUI delays.
        pyautogui.PAUSE = 0
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        apply_app_icon(self.root)
        self._setup_fullscreen_controls()

        self.is_running = False
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.state_lock = threading.Lock()
        self.last_toggle_time = 0.0
        self.hotkey_hook = None
        self.hotkey_binding = None
        self.hotkey_is_down = False
        self.is_recording_hotkey = False
        self.color_pick_thread = None
        self.color_pick_in_progress = False
        self.is_closing = False
        self.cleanup_done = False
        self.backend_name = "unknown"
        self.last_error = None
        self._updating_color_inputs = False

        self.config_path = _get_user_config_path()
        self.config = self.load_config()
        # `self.settings` points to this tool's section inside the shared config file.
        self.settings = self.config.setdefault(
            self.CONFIG_SECTION, self.DEFAULT_CONFIG.copy()
        )
        self.colors = self._normalize_color_list(self.settings)
        self.selected_color_index = 0

        self.current_hotkey = self._normalize_hotkey(
            self.settings.get("hotkey", self.DEFAULT_CONFIG["hotkey"])
        )
        self._init_win32_apis()

        self._build_ui()
        self.bind_hotkey()
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.root.bind("<Destroy>", self._on_root_destroy, add="+")

    def _setup_fullscreen_controls(self):
        """Bind keyboard shortcuts related to window mode."""
        self.root.bind("<F11>", lambda event: self.toggle_fullscreen(), add="+")

    def toggle_fullscreen(self):
        """Toggle Tk fullscreen attribute on/off."""
        self.root.attributes("-fullscreen", not bool(self.root.attributes("-fullscreen")))

    # ------------------------ UI ------------------------
    def _build_ui(self):
        """Build all UI sections in display order."""
        ttk.Label(self.root, text="Colour Seeking Cursor",
                  font=("Segoe UI", 13, "bold")).pack(pady=10)
        ttk.Label(self.root, text="Jumps the mouse to a selected color on the screen closest to the cursor").pack(pady=5)
        ttk.Label(self.root, text="not recommended to use without a shortcut key (controls your mouse)").pack(pady=5)

        self._build_color_controls()
        self._build_tolerance_control()
        self._build_cluster_size_control()
        self._build_buttons()
        self._build_status()
        self._build_hotkey_section()
        
    def _build_color_controls(self):
        """Build color list, color action buttons, and RGB editors."""
        ttk.Label(self.root, text="Tracked Colours (RGB)").pack(pady=5)

        list_frame = ttk.Frame(self.root)
        list_frame.pack(padx=20, pady=(5, 0), fill=tk.BOTH)

        # Treeview lets us attach an image per row, so swatch color stays correct
        # even when the row is selected.
        self.color_listbox = ttk.Treeview(list_frame, show="tree", selectmode="browse", height=4)
        self.color_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.color_listbox.bind("<<TreeviewSelect>>", self.on_color_select)
        # Keep references to PhotoImage objects to prevent garbage collection.
        self.color_swatch_images = []

        controls = ttk.Frame(list_frame)
        controls.pack(side=tk.LEFT, padx=(8, 0), fill=tk.Y)
        ttk.Button(controls, text="Add", command=self.add_color_combination).pack(fill=tk.X, pady=2)
        ttk.Button(controls, text="Delete", command=self.delete_color_combination).pack(fill=tk.X, pady=2)
        ttk.Button(controls, text="Pick From Wheel", command=self.pick_color_from_wheel).pack(fill=tk.X, pady=2)
        ttk.Button(controls, text="Pick From Screen", command=self.pick_color_from_screen).pack(fill=tk.X, pady=2)

        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=8, fill=tk.X)

        selected = self.colors[self.selected_color_index]
        self.r_var = tk.IntVar(value=selected["r"])
        self.g_var = tk.IntVar(value=selected["g"])
        self.b_var = tk.IntVar(value=selected["b"])

        for label, var in (("R", self.r_var), ("G", self.g_var), ("B", self.b_var)):
            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT, padx=5)
            ttk.Spinbox(frame, from_=0, to=255, width=5, textvariable=var).pack(side=tk.LEFT, padx=5)

        # `trace_add("write", ...)` means "call this function whenever the variable changes".
        # This catches both user edits and code-driven `.set(...)` updates.
        self.r_var.trace_add("write", self.on_color_value_changed)
        self.g_var.trace_add("write", self.on_color_value_changed)
        self.b_var.trace_add("write", self.on_color_value_changed)
        self._refresh_color_listbox()

    def _build_tolerance_control(self):
        """Build slider that controls color match tolerance."""
        # Tolerance controls how far a screen pixel can be from a target color and still count as a match.
        self.tolerance_label_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.tolerance_label_var).pack(pady=5)
        self.tolerance_var = tk.DoubleVar(value=self.settings.get("tolerance", 100))
        self.tolerance_var.trace_add("write", self.on_tolerance_changed)
        self._update_tolerance_label()
        ttk.Scale(
            self.root, from_=10, to=255, orient=tk.HORIZONTAL, variable=self.tolerance_var
        ).pack(padx=20, fill=tk.X)

    def _build_cluster_size_control(self):
        """Build slider that ignores clusters smaller than a threshold."""
        # Ignore tiny color blobs to reduce jumps to noise/single pixels.
        self.cluster_size_label_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.cluster_size_label_var).pack(pady=5)
        self.min_cluster_size_var = tk.DoubleVar(value=self.settings.get("min_cluster_size", 3))
        self.min_cluster_size_var.trace_add("write", self.on_min_cluster_size_changed)
        self._update_min_cluster_size_label()
        ttk.Scale(
            self.root, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.min_cluster_size_var
        ).pack(padx=20, fill=tk.X)

    def _build_buttons(self):
        """Build Start/Stop controls for the seeking worker."""
        frame = ttk.Frame(self.root)
        frame.pack(pady=15, padx=20, fill=tk.X)
        ttk.Button(frame, text="Start", command=self.start_seeking).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(frame, text="Stop", command=self.stop_seeking).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _build_status(self):
        """Build status label shown during runtime."""
        self.status_label = ttk.Label(self.root, text="Status: Stopped", foreground="red")
        self.status_label.pack(pady=10)

    def _build_hotkey_section(self):
        """Build hotkey display and hotkey configuration buttons."""
        ttk.Separator(self.root).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(self.root, text="Hotkey Settings", font=("Segoe UI", 10, "bold")).pack(pady=5)
        frame = ttk.Frame(self.root)
        frame.pack(padx=20, pady=5, fill=tk.X)

        self.hotkey_display = ttk.Entry(frame, state="readonly")
        self.hotkey_display.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.update_hotkey_display()

        ttk.Button(frame, text="Bind a shortcut key", command=self.record_hotkey).pack(side=tk.LEFT)
        ttk.Button(frame, text="Reset to default", command=self.reset_hotkey).pack(side=tk.LEFT)
        self.record_label = ttk.Label(self.root, foreground="blue")
        self.record_label.pack(pady=5)

    # ------------------------ Config ------------------------
    def load_config(self) -> dict:
        """Load app config JSON from disk; return empty dict on failure."""
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _normalize_color_component(self, value, fallback=0):
        """Convert a value to RGB component range 0..255."""
        try:
            return max(0, min(255, int(value)))
        except Exception:
            return fallback

    def _normalize_color_list(self, settings):
        """Read color list from settings and normalize each RGB component."""
        raw = settings.get("colors")
        colors = []
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                colors.append({
                    "r": self._normalize_color_component(item.get("r", 0)),
                    "g": self._normalize_color_component(item.get("g", 0)),
                    "b": self._normalize_color_component(item.get("b", 0)),
                })

        # Backward compatibility for old single-color configs
        if not colors:
            colors = [{
                "r": self._normalize_color_component(settings.get("target_r", 255), 255),
                "g": self._normalize_color_component(settings.get("target_g", 0), 0),
                "b": self._normalize_color_component(settings.get("target_b", 0), 0),
            }]
        return colors

    def save_config(self):
        """Write full config dictionary to disk."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    # ------------------------ Seeking ------------------------
    def start_seeking(self):
        """Start background scanning thread if not already running."""
        if self.is_closing:
            return
        with self.state_lock:
            if self.is_running:
                return
            self.is_running = True
            self.stop_event.clear()
            # Background thread keeps UI responsive while we scan pixels continuously.
            worker = threading.Thread(target=self.seeking_loop, daemon=True)
            self.worker_thread = worker
        self._set_runtime_status("Status: Seeking", "green")
        worker.start()

    def stop_seeking(self, update_status: bool = True):
        """Signal worker to stop and optionally update UI status."""
        with self.state_lock:
            self.is_running = False
            self.stop_event.set()
            worker = self.worker_thread
            self.worker_thread = None
        if worker and worker.is_alive() and worker is not threading.current_thread():
            worker.join(timeout=self.STOP_JOIN_TIMEOUT)
        if update_status and not self.is_closing:
            self._set_status("Status: Stopped", "red")

    def seeking_loop(self):
        """Worker loop: repeatedly execute seek steps until stopped."""
        try:
            while not self.stop_event.is_set():
                try:
                    self._seek_step()
                except Exception as e:
                    self.last_error = str(e)
                    if not self.stop_event.is_set() and not self.is_closing:
                        self._set_runtime_status(f"Status: Error ({self.last_error[:60]})", "red")

                if self.stop_event.wait(timeout=self.LOOP_DELAY):
                    break
        finally:
            with self.state_lock:
                if threading.current_thread() is self.worker_thread:
                    self.worker_thread = None
                self.is_running = False

    def _seek_step(self):
        """Capture area, find color clusters, then move mouse to nearest valid cluster."""
        if self.stop_event.is_set() or not self.is_running or self.is_closing:
            return

        targets = [(c["r"], c["g"], c["b"]) for c in self.colors]
        tolerance = self.tolerance_var.get()
        min_cluster_size = max(1, int(round(float(self.min_cluster_size_var.get()))))

        cx, cy = pyautogui.position()
        virtual_bounds = self._get_virtual_screen_bounds()
        win_left, win_top, win_right, win_bottom = self._get_cursor_window_bounds(virtual_bounds)

        width = win_right - win_left + 1
        height = win_bottom - win_top + 1
        if width <= 0 or height <= 0:
            return

        try:
            # ImageGrab supports virtual desktop coordinates (including negative coordinates).
            screenshot = ImageGrab.grab(
                bbox=(win_left, win_top, win_right + 1, win_bottom + 1),
                all_screens=True
            )
            pixels = screenshot.load()
        except Exception:
            if not self.stop_event.is_set() and not self.is_closing:
                self._set_runtime_status("Status: Screenshot failed", "red")
            return

        x_samples = list(range(0, width, self.SAMPLE_STEP))
        y_samples = list(range(0, height, self.SAMPLE_STEP))
        if not x_samples or not y_samples:
            return

        # 2D grid of True/False where True means this sampled point is close enough to target color.
        match_mask = [[False] * len(x_samples) for _ in range(len(y_samples))]

        for gy, y in enumerate(y_samples):
            if self.stop_event.is_set() or not self.is_running or self.is_closing:
                return
            for gx, x in enumerate(x_samples):
                r, g, b = pixels[x, y][:3]
                color_distance = min(math.dist((r, g, b), target) for target in targets)
                if color_distance <= tolerance:
                    match_mask[gy][gx] = True

        if self.stop_event.is_set() or not self.is_running or self.is_closing:
            return

        clusters = self._find_color_clusters(
            match_mask=match_mask,
            x_samples=x_samples,
            y_samples=y_samples,
            win_left=win_left,
            win_top=win_top
        )

        if self.stop_event.is_set() or not self.is_running or self.is_closing:
            return

        if clusters:
            # Filter out tiny clusters first; they are usually noise.
            eligible_clusters = [cluster for cluster in clusters if cluster[2] >= min_cluster_size]
            if not eligible_clusters:
                self._set_runtime_status(
                    f"Status: found density not bigger than {min_cluster_size}",
                    "orange"
                )
                return

            center_x, center_y, cluster_size = min(
                eligible_clusters,
                # Pick the cluster center closest to current mouse position.
                key=lambda cluster: math.hypot(cluster[0] - cx, cluster[1] - cy)
            )
            
            if cluster_size < 3:
                self.Strength = "Negligible"
            elif cluster_size < 30:
                self.Strength = "Very Low"
            elif cluster_size < 80:
                self.Strength = "Low"
            elif cluster_size < 150:
                self.Strength = "Modest"    
            elif cluster_size < 250:
                self.Strength = "Moderate"
            elif cluster_size < 500: 
                self.Strength = "High"
            elif cluster_size < 1000:
                self.Strength = "Very High"
            elif cluster_size < 5000:
                self.Strength = "Ultra High"
            elif cluster_size < 7500:
                self.Strength = "Extremely High"
            elif cluster_size < 10000:
                self.Strength = "Extremely High+"
            elif cluster_size < 30000:
                self.Strength = "Extremely High++"
            else:
                self.Strength = "Extremely High+++"
                        
            
            # Instant jump directly to the chosen cluster center.
            pyautogui.moveTo(center_x, center_y)
            self._set_runtime_status(
                f"Status: Seeking (pixel density: {cluster_size}  {self.Strength})",
                "green"
            )
        else:
            self._set_runtime_status("Status: No match found", "orange")

    def _find_color_clusters(self, match_mask, x_samples, y_samples, win_left, win_top):
        """Find connected groups in the match grid and return each group's center."""
        clusters = []
        grid_h = len(match_mask)
        grid_w = len(match_mask[0]) if grid_h else 0
        if grid_w == 0:
            return clusters

        # Standard flood-fill (DFS) bookkeeping so each cell is processed once.
        visited = [[False] * grid_w for _ in range(grid_h)]
        neighbors = (
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),            (1, 0),
            (-1, 1),  (0, 1),   (1, 1),
        )
        
        for gy in range(grid_h):
            if self.stop_event.is_set() or not self.is_running or self.is_closing:
                return []
            for gx in range(grid_w):
                if visited[gy][gx] or not match_mask[gy][gx]:
                    continue

                stack = [(gx, gy)]
                visited[gy][gx] = True
                pixel_count = 0
                sum_x = 0.0
                sum_y = 0.0

                while stack:
                    cx, cy = stack.pop()
                    pixel_count += 1
                    # Convert sample-grid coordinates back to real screen coordinates.
                    sum_x += win_left + x_samples[cx]
                    sum_y += win_top + y_samples[cy]

                    for dx, dy in neighbors:
                        nx = cx + dx
                        ny = cy + dy
                        if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
                            continue
                        if visited[ny][nx] or not match_mask[ny][nx]:
                            continue
                        visited[ny][nx] = True
                        stack.append((nx, ny))

                if pixel_count > 0:
                    # Cluster center is the average of all points in this connected component.
                    clusters.append((
                        int(round(sum_x / pixel_count)),
                        int(round(sum_y / pixel_count)),
                        pixel_count
                    ))

        return clusters

    def _init_win32_apis(self):
        """Prepare Win32 function signatures used for cursor/window queries."""
        self.user32 = ctypes.windll.user32
        self.user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.user32.GetCursorPos.restype = wintypes.BOOL
        self.user32.WindowFromPoint.argtypes = [wintypes.POINT]
        self.user32.WindowFromPoint.restype = wintypes.HWND
        self.user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = wintypes.HWND
        self.user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetWindowRect.restype = wintypes.BOOL

    def _get_virtual_screen_bounds(self):
        """Return full virtual desktop bounds across all monitors."""
        SM_XVIRTUALSCREEN = 76
        SM_YVIRTUALSCREEN = 77
        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79
        left = self.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        top = self.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        width = self.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = self.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
        right = left + width - 1
        bottom = top + height - 1
        return left, top, right, bottom

    def _clip_window_bounds(self, rect: wintypes.RECT, virtual_bounds):
        """Clamp a window rect so it stays inside virtual screen bounds."""
        v_left, v_top, v_right, v_bottom = virtual_bounds
        left = max(v_left, min(v_right, rect.left))
        top = max(v_top, min(v_bottom, rect.top))
        right = max(v_left, min(v_right, rect.right - 1))
        bottom = max(v_top, min(v_bottom, rect.bottom - 1))
        return left, top, right, bottom

    def _get_cursor_window_bounds(self, virtual_bounds):
        """Return bounds for the top-level window currently under the cursor."""
        try:
            point = wintypes.POINT()
            if not self.user32.GetCursorPos(ctypes.byref(point)):
                raise RuntimeError("GetCursorPos failed")

            hwnd = self.user32.WindowFromPoint(point)
            if not hwnd:
                raise RuntimeError("WindowFromPoint failed")

            GA_ROOT = 2
            root_hwnd = self.user32.GetAncestor(hwnd, GA_ROOT)
            if root_hwnd:
                hwnd = root_hwnd

            rect = wintypes.RECT()
            if not self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                raise RuntimeError("GetWindowRect failed")

            left, top, right, bottom = self._clip_window_bounds(rect, virtual_bounds)

            if right < left or bottom < top:
                raise RuntimeError("Invalid window bounds")

            return left, top, right, bottom
        except Exception:
            return virtual_bounds

    # ------------------------ Hotkeys ------------------------
    def _normalize_hotkey(self, hotkey: str) -> str:
        """Normalize hotkey text to a safe lowercase format."""
        if not hotkey:
            return self.DEFAULT_CONFIG["hotkey"]
        normalized = str(hotkey).strip().lower()
        if normalized.startswith("<") and normalized.endswith(">"):
            normalized = normalized[1:-1].strip()
        return normalized or self.DEFAULT_CONFIG["hotkey"]

    def _is_single_key_hotkey(self, hotkey: str) -> bool:
        """Return True if hotkey is a single key (no combo separators)."""
        return "+" not in hotkey and "," not in hotkey

    def _handle_single_key_hotkey_event(self, event):
        """Handle press/release events for single-key hotkey mode."""
        if self.is_closing or self.is_recording_hotkey:
            return
        if event.event_type == "down":
            if self.hotkey_is_down:
                return
            self.hotkey_is_down = True
            self.toggle_seeking()
        elif event.event_type == "up":
            self.hotkey_is_down = False

    def bind_hotkey(self):
        """Bind current hotkey via keyboard library."""
        if self.is_closing:
            return
        self._safe_remove_hotkey_binding()

        hotkey = self._normalize_hotkey(self.current_hotkey)
        self.current_hotkey = hotkey
        self.settings["hotkey"] = hotkey

        try:
            # `hook_key` supports key-down and key-up events for debounced single-key toggles.
            if self._is_single_key_hotkey(hotkey):
                self.hotkey_binding = keyboard.hook_key(hotkey, self._handle_single_key_hotkey_event)
            else:
                # For combos (e.g. ctrl+alt+k), a simple callback binding is enough.
                self.hotkey_binding = keyboard.add_hotkey(hotkey, self.toggle_seeking)
        except Exception as e:
            if not self.is_closing:
                self._set_status(f"Status: Hotkey error ({e})", "red")

    def toggle_seeking(self):
        """Toggle start/stop state with debounce protection."""
        if self.is_closing or self.is_recording_hotkey:
            return
        now = time.monotonic()
        if (now - self.last_toggle_time) < self.TOGGLE_DEBOUNCE:
            return
        self.last_toggle_time = now
        self._safe_after(self._toggle_seeking_main_thread)

    def _toggle_seeking_main_thread(self):
        """Execute start/stop toggle on Tk main thread."""
        if self.is_closing:
            return
        if self.is_running:
            self.stop_seeking()
        else:
            self.start_seeking()

    def record_hotkey(self):
        """Capture next pressed key and store it as the new hotkey."""
        if self.is_closing:
            return
        self.is_recording_hotkey = True
        self._safe_remove_hotkey_binding()
        self.record_label.config(text="Press desired hotkey...")
        self._safe_remove_hotkey_hook()

        def on_key(event):
            # Keyboard callbacks happen outside Tk thread; apply changes through `_safe_after`.
            if event.event_type != "down" or self.is_closing:
                return
            captured_hotkey = self._normalize_hotkey(event.name)

            def apply_hotkey():
                if self.is_closing:
                    return
                self.current_hotkey = captured_hotkey
                self.update_hotkey_display()
                self.bind_hotkey()
                self.is_recording_hotkey = False
                self.record_label.config(text="")
                self._safe_remove_hotkey_hook()
                self.save_settings()

            self._safe_after(apply_hotkey)

        try:
            self.hotkey_hook = keyboard.hook(on_key)
        except Exception as e:
            self.is_recording_hotkey = False
            self.bind_hotkey()
            self._set_status(f"Status: Hotkey record error ({e})", "red")

    def reset_hotkey(self):
        """Reset hotkey to built-in default."""
        if self.is_closing:
            return
        self.current_hotkey = self.DEFAULT_CONFIG["hotkey"]
        self.update_hotkey_display()
        self.bind_hotkey()
        self.save_settings()

    def update_hotkey_display(self):
        """Refresh read-only entry to show current hotkey text."""
        try:
            self.hotkey_display.config(state="normal")
            self.hotkey_display.delete(0, tk.END)
            self.hotkey_display.insert(0, self.current_hotkey)
            self.hotkey_display.config(state="readonly")
        except tk.TclError:
            pass

    # ------------------------ Status ------------------------
    def _set_status(self, text: str, color: str):
        """Set status label text/color safely on Tk thread."""
        def apply():
            try:
                self.status_label.config(text=text, foreground=color)
            except tk.TclError:
                pass
        self._safe_after(apply)

    def _set_runtime_status(self, text: str, color: str):
        """Set status during runtime, unless app is stopping/closing."""
        if self.stop_event.is_set() or self.is_closing:
            return

        def apply():
            if self.stop_event.is_set() or self.is_closing:
                return
            try:
                self.status_label.config(text=text, foreground=color)
            except tk.TclError:
                pass

        self._safe_after(apply)

    # ------------------------ Colour List ------------------------
    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB integers to '#RRGGBB' string."""
        return f"#{r:02x}{g:02x}{b:02x}"

    def _make_color_swatch(self, r: int, g: int, b: int) -> tk.PhotoImage:
        # Solid square image used in Treeview rows as the color icon.
        image = tk.PhotoImage(width=12, height=12)
        image.put(self._rgb_to_hex(r, g, b), to=(0, 0, 12, 12))
        return image

    def _refresh_color_listbox(self):
        """Rebuild color rows, keep selection valid, and sync RGB inputs."""
        self.color_listbox.delete(*self.color_listbox.get_children())
        self.color_swatch_images = []
        for index, color in enumerate(self.colors):
            swatch = self._make_color_swatch(color["r"], color["g"], color["b"])
            self.color_swatch_images.append(swatch)
            row_text = f'RGB({color["r"]}, {color["g"]}, {color["b"]})'
            self.color_listbox.insert("", "end", iid=str(index), text=row_text, image=swatch)

        if self.selected_color_index >= len(self.colors):
            self.selected_color_index: int = len(self.colors) - 1
        if self.selected_color_index < 0:
            self.selected_color_index = 0
        selected_iid = str(self.selected_color_index)
        self.color_listbox.selection_set(selected_iid)
        self.color_listbox.focus(selected_iid)
        self.color_listbox.see(selected_iid)
        self._load_selected_color_into_inputs()

    def _load_selected_color_into_inputs(self):
        """Copy selected color from list into R/G/B Tk variables."""
        if not self.colors:
            return
        # Guard flag prevents `trace_add` callbacks from treating these `.set(...)`
        # calls as user edits and writing back immediately.
        self._updating_color_inputs = True
        selected = self.colors[self.selected_color_index]
        self.r_var.set(selected["r"])
        self.g_var.set(selected["g"])
        self.b_var.set(selected["b"])
        self._updating_color_inputs = False

    def on_color_select(self, event=None):
        """Handle list selection changes and load selected color to inputs."""
        selection = self.color_listbox.selection()
        if not selection:
            return
        self.selected_color_index = int(selection[0])
        self._load_selected_color_into_inputs()

    def on_color_value_changed(self, *args):
        """Persist RGB edits from spinboxes into selected color entry."""
        if self._updating_color_inputs or self.is_closing:
            return
        if not self.colors:
            return
        self.colors[self.selected_color_index] = {
            "r": self._normalize_color_component(self.r_var.get()),
            "g": self._normalize_color_component(self.g_var.get()),
            "b": self._normalize_color_component(self.b_var.get()),
        }
        self._refresh_color_listbox()
        self.save_settings()

    def on_tolerance_changed(self, *args):
        """Handle tolerance slider changes."""
        if self.is_closing:
            return
        self._update_tolerance_label()
        self.save_settings()

    def on_min_cluster_size_changed(self, *args):
        """Handle minimum-cluster slider changes."""
        if self.is_closing:
            return
        self._update_min_cluster_size_label()
        self.save_settings()

    def _update_tolerance_label(self):
        """Refresh tolerance label text from slider value."""
        try:
            value = int(round(float(self.tolerance_var.get())))
        except Exception:
            value = 0
        self.tolerance_label_var.set(
            f"Color Tolerance (lower the more stricter): {value}"
        )

    def _update_min_cluster_size_label(self):
        """Refresh minimum cluster size label text from slider value."""
        try:
            value = max(1, int(round(float(self.min_cluster_size_var.get()))))
        except Exception:
            value = 1
        self.cluster_size_label_var.set(
            f"Minimum Cluster Size (higher the more demanding): {value}"
        )

    def add_color_combination(self):
        """Append a new color (copy of current) and select it."""
        if self.is_closing:
            return
        base = self.colors[self.selected_color_index] if self.colors else {"r": 255, "g": 0, "b": 0}
        self.colors.append(dict(base))
        self.selected_color_index = len(self.colors) - 1
        self._refresh_color_listbox()
        self.save_settings()

    def delete_color_combination(self):
        """Delete selected color if more than one color remains."""
        if self.is_closing:
            return
        if len(self.colors) <= 1:
            messagebox.showwarning(
                "Warning",
                "unable to delete colour (must have atleast one colour)"
            )
            return
        self.colors.pop(self.selected_color_index)
        if self.selected_color_index >= len(self.colors):
            self.selected_color_index = len(self.colors) - 1
        self._refresh_color_listbox()
        self.save_settings()

    def pick_color_from_wheel(self):
        """Open color picker dialog and apply chosen color."""
        if self.is_closing or not self.colors:
            return

        selected = self.colors[self.selected_color_index]
        initial_hex = self._rgb_to_hex(selected["r"], selected["g"], selected["b"])

        # Prefer tkcolorpicker's wheel, and fall back to Tk's chooser.
        rgb = None
        if wheel_askcolor is not None:
            result = wheel_askcolor(color=initial_hex, parent=self.root, title="Pick colour")
            if result and result[0] is not None:
                rgb = result[0]
        else:
            result = colorchooser.askcolor(color=initial_hex, parent=self.root, title="Pick colour")
            if result and result[0] is not None:
                rgb = result[0]

        if rgb is None:
            # User canceled dialog.
            return

        r, g, b = [self._normalize_color_component(int(round(value))) for value in rgb]
        self._apply_picked_color((r, g, b))

    def pick_color_from_screen(self):
        """Temporarily hide app and pick color from next screen click."""
        if self.is_closing or self.color_pick_in_progress:
            return

        if self.is_running:
            self.stop_seeking()

        self.color_pick_in_progress = True
        self._set_status("Status: Click anywhere to pick colour", "blue")
        try:
            self.root.withdraw()
        except tk.TclError:
            self.color_pick_in_progress = False
            return

        # Run click-wait logic in background so UI thread does not block.
        self.color_pick_thread = threading.Thread(target=self._pick_color_worker, daemon=True)
        self.color_pick_thread.start()

    def _pick_color_worker(self):
        """Wait for left-click, sample pixel under cursor, then apply picked color."""
        try:
            VK_LBUTTON = 0x01
            was_down = False
            while not self.is_closing:
                is_down = bool(self.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
                if is_down and not was_down:
                    # Detect edge: "just pressed now" (not held from previous loop).
                    point = wintypes.POINT()
                    if not self.user32.GetCursorPos(ctypes.byref(point)):
                        break
                    picked = self._sample_screen_pixel(point.x, point.y)
                    if picked is not None:
                        self._safe_after(lambda rgb=picked: self._apply_picked_color(rgb))
                    break
                was_down = is_down
                time.sleep(0.01)
        finally:
            self._safe_after(self._finish_color_pick)

    def _sample_screen_pixel(self, screen_x: int, screen_y: int):
        """Sample one screen pixel in virtual-desktop coordinate space."""
        try:
            v_left, v_top, _, _ = self._get_virtual_screen_bounds()
            image = ImageGrab.grab(all_screens=True)
            px = screen_x - v_left
            py = screen_y - v_top
            if px < 0 or py < 0 or px >= image.width or py >= image.height:
                return None
            r, g, b = image.getpixel((px, py))[:3]
            return int(r), int(g), int(b)
        except Exception:
            return None

    def _apply_picked_color(self, rgb):
        """Write picked RGB value into currently selected color."""
        if self.is_closing or not self.colors:
            return
        r, g, b = rgb
        self.colors[self.selected_color_index] = {"r": r, "g": g, "b": b}
        self._refresh_color_listbox()
        self.save_settings()
        self._set_status("Status: Colour picked", "green")
        self.root.after(3100, lambda: self._set_status("Status: Stopped", "red") if not self.is_running else None)
        

    def _finish_color_pick(self):
        """Restore app window state after screen-pick workflow ends."""
        self.color_pick_in_progress = False
        
        if self.is_closing:
            return
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
        except tk.TclError:
            pass

    def _safe_after(self, callback):
        # Tk widgets must be touched from the main Tk thread.
        # This schedules `callback` safely on that thread.
        try:
            self.root.after(0, callback)
            return True
        
        except tk.TclError:
            return False 
        
    
        
    def _safe_remove_hotkey_binding(self):
        """Best-effort removal of active hotkey binding object."""
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

    def _safe_remove_hotkey_hook(self):
        """Best-effort removal of keyboard hook used during hotkey recording."""
        if not self.hotkey_hook:
            return
        try:
            keyboard.unhook(self.hotkey_hook)
        except Exception:
            pass
        finally:
            self.hotkey_hook = None

    def _update_settings_from_ui(self):
        """Copy current UI values into in-memory settings dictionary."""
        # Copy live UI state into the config dict that is written to disk.
        self.settings.update(
            hotkey=self._normalize_hotkey(self.current_hotkey),
            colors=[dict(color) for color in self.colors],
            tolerance=self.tolerance_var.get(),
            min_cluster_size=max(1, int(round(float(self.min_cluster_size_var.get()))))
        )

    # ------------------------ Save / Close ------------------------
    def save_settings(self):
        """Update settings from UI and persist them to disk."""
        try:
            self._update_settings_from_ui()
            
        except tk.TclError:
            return
        self.save_config()

    def _cleanup(self, persist_settings: bool):
        """One-time shutdown sequence for worker threads and hotkeys."""
        if self.cleanup_done:
            return
        self.cleanup_done = True
        self.is_closing = True
        self.stop_seeking(update_status=False)
        self._safe_remove_hotkey_hook()
        self._safe_remove_hotkey_binding()
        if persist_settings:
            self.save_settings()

    def _on_root_destroy(self, event):
        """Handle Tk destroy event to clean up resources safely."""
        if event.widget is self.root:
            self._cleanup(persist_settings=False)

    def on_window_close(self):
        """Handle window close button and persist settings."""
        self._cleanup(persist_settings=True)
        try:
            self.root.destroy()
        except tk.TclError:
            pass

# ------------------------ Run ------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ColourSeekingCursor(root)
    root.mainloop()
