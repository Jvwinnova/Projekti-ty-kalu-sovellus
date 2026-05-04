import tkinter as tk
from tkinter import ttk
import time

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Kmh:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("kilometers per hour")
        self.root.geometry("420x300")
        self.root.resizable(True, True)
        apply_app_icon(self.root)

        self.meterstravelled = 0
        self.kilometerstravelled = 0
        self.kmph = 0
        self.secondstravelled = 0
        self.travelling = False

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Kilometers per hour",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 12))

        kmph_entry = ttk.Entry(container)
        kmph_entry.pack(pady=10)
        kmph_entry.bind("<KeyRelease>", self.set_kmph)

        self.distance_label = ttk.Label(
            container,
            text=f"Distance traveled: {self.kilometerstravelled:.2f} km, {self.meterstravelled:.2f} m",
            wraplength=360,
            justify="center",
        )
        self.distance_label.pack(expand=True)

        self.seconds_label = ttk.Label(
            container,
            text=f"Time traveled: {self.format_time(self.secondstravelled)}",
            wraplength=360,
            justify="center",
        )
        self.seconds_label.pack(expand=True)
        #buttons to start, stop and reset the traveling session
        ttk.Button(container, text="start traveling", command=self.travel).pack(pady=10)
        ttk.Button(container, text="stop traveling", command=self.stop).pack(pady=10)
        ttk.Button(container, text="reset", command=self.reset).pack(pady=10)
    #format time to use it in our label to show user how long they have been traveling
    def format_time(self, seconds):
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def set_kmph(self, event):
        try:
            self.kmph = float(event.widget.get())
        except ValueError:
            self.kmph = 0

    def travel(self):
        self.travelling = True
        self._last_time = None
        self._travel_loop()

    def _travel_loop(self):
        if not self.travelling:
            return

        now = time.time()

        if self._last_time is not None:
            dt = now - self._last_time

            speed_m_per_s = self.kmph * (1000 / 3600)
            self.meterstravelled += speed_m_per_s * dt
            self.kilometerstravelled = self.meterstravelled / 1000
            self.secondstravelled += dt
            #show the distance traveled and time traveled in the label
            self.distance_label.config(
                text=f"Distance traveled: {self.kilometerstravelled:.2f} km, {self.meterstravelled:.2f} m"
            )
            # use the format_time function to show time in a nice format
            self.seconds_label.config(
                text=f"Time traveled: {self.format_time(self.secondstravelled)}"
            )

        self._last_time = now
        self.root.after(50, self._travel_loop)

    def stop(self):
        self.travelling = False
        self._last_time = None

    def reset(self):
        self.stop()
        self.meterstravelled = 0
        self.kilometerstravelled = 0
        self.secondstravelled = 0

        self.distance_label.config(
            text=f"Distance traveled: {self.kilometerstravelled:.2f} km, {self.meterstravelled:.2f} m"
        )

        self.seconds_label.config(
            text=f"Time traveled: {self.format_time(self.secondstravelled)}"
        )


def run():
    root = tk.Tk()
    Kmh(root)
    root.mainloop()


if __name__ == "__main__":
    run()