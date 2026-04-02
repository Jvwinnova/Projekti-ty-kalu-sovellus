import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import audioplayer
try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class MusicFile:
    """Empty tool template wired to the UI."""
    audiopaused = False
    audioplaying = False
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Music player")
        self.root.geometry("480x300")
        self.root.resizable(True, True)
        self.player = None
        self.selected_file = None
        apply_app_icon(self.root)
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Music Player",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 8))

        ttk.Label(
            container,
            text="play mp3 files here",
            wraplength=440,
        ).pack()

        ttk.Button(container, text="Choose MP3", command=self._choose_file).pack(pady=(16, 8))
        
        self.file_label = ttk.Label(
            container,
            text="No file selected",
            wraplength=440,
        )
        self.file_label.pack()
        
        ttk.Button(container, text="Play audio", command=self._play_audio).pack(pady=(16, 0))
        ttk.Button(container, text="Pause audio", command=self._pause_audio).pack(pady=(8, 0))
        ttk.Button(container, text="Stop audio", command=self._stop_audio).pack(pady=(8, 0))
        
    def _choose_file(self):
        # Restrict the picker to MP3 files so users only choose supported tracks.
        selected_file = filedialog.askopenfilename(
            title="Choose an MP3 file",
            filetypes=[("MP3 files", "*.mp3")],
        )
        if not selected_file:
            return

        self.selected_file = Path(selected_file)
        self.file_label.config(text=self.selected_file.name)

    def _play_audio(self):
        if self.audiopaused:
            self.player.resume()
            self.audiopaused = False
            self.audioplaying = True
            print("Audio resumed.")
        else:
            # Fall back to the bundled sample track until the user chooses a file.
            audio_path = self.selected_file or Path(__file__).resolve().parents[4] / "assets" / "mactonight.mp3"

            # Keep the player on self so the object is not discarded during playback.
            self.player = audioplayer.AudioPlayer(str(audio_path))
            self.player.play()
            self.audiopaused = False
            self.audioplaying = True
            print("Playing audio...")
    def _pause_audio(self):
        if self.player:
            self.player.pause()
            self.audiopaused = True
            self.audioplaying = False
            print("Audio paused.")
    def _stop_audio(self):
        if self.player:
            self.player.stop()
            self.audiopaused = False
            self.audioplaying = False
            print("Audio stopped.")

def run():
    root = tk.Tk()
    MusicFile(root)
    root.mainloop()


if __name__ == "__main__":
    run()
