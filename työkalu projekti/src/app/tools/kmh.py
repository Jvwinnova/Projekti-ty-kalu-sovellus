import tkinter as tk
from tkinter import ttk

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Kmh:
    """Minimal tool window template."""

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
            text=f"Distance traveled: {self.kilometerstravelled:.2f} kilometers, {self.meterstravelled} meters",
            wraplength=360,
            justify="center",
        )
        self.distance_label.pack(expand=True)

       
        self.seconds_label = ttk.Label(
            container,
            text=f"Time traveled: {self.secondstravelled} seconds",
            wraplength=360,
            justify="center",
        )
        self.seconds_label.pack(expand=True)

        travel_button = ttk.Button(container, text="start traveling", command=self.travel)
        travel_button.pack(pady=10)

        stop_button = ttk.Button(container, text="stop traveling", command=self.stop)
        stop_button.pack(pady=10)

        reset_button = ttk.Button(container, text="reset", command=self.reset)
        reset_button.pack(pady=10)

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

        import time
        now = time.time()

        if self._last_time is not None:
            dt = now - self._last_time  # seconds since last update

            speed_m_per_s = self.kmph * (1000 / 3600)
            self.meterstravelled += speed_m_per_s * dt
            self.kilometerstravelled = self.meterstravelled / 1000
            self.secondstravelled += dt
            self.distance_label.config(
                text=f"Distance traveled: {self.kilometerstravelled:.2f} kilometers, {self.meterstravelled:.2f} meters"
            )
           
            self.seconds_label.config(
                text=f"Time traveled: {self.secondstravelled:.2f} seconds"
            )

        self._last_time = now

        # update every 50 ms (~20 updates/sec)
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
            text=f"Distance traveled: {self.kilometerstravelled:.2f} kilometers, {self.meterstravelled:.2f} meters"
        )
        self.seconds_label.config(
            text=f"Time traveled: {self.secondstravelled:.2f} seconds"
        )

        

def run():
    root = tk.Tk()
    Kmh(root)
    root.mainloop()


if __name__ == "__main__":
    run()
