"""Small notepad-style editor with save and save-as support."""

import os
import tkinter as tk
from tkinter import ttk
import json
from tkinter import filedialog
try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


def _get_user_config_path():
    """Return the shared user config path for storing saved text."""
    base_dir = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(base_dir, "ToolKit")
    return os.path.join(config_dir, "config.json")


class Write:
    """Edit a text buffer, save it to config, or export it to a file."""

    default_config = {
        "Write": {
            "savestring": ""
        }
    }

    def __init__(self, root: tk.Tk):
        self.config_path = _get_user_config_path()
        self.config = self._load_config()

        self.root = root
        self.root.title("Write")
        self.root.geometry("800x400")
        self.root.resizable(True, True)
        apply_app_icon(self.root)

        self._build_ui()

    def _build_ui(self):
        """Create editor actions and the main text widget."""
        write_button = ttk.Button(
            self.root, text="edit", command=self._on_enable_entry
        )
        save_button = ttk.Button(
            self.root, text="save", command=self._on_save_entry
        )
        save_as_button = ttk.Button(
            self.root, text="save as", command=self._on_save_as_entry
        )
        write_button.pack(pady=2)
        save_button.pack(pady=2)
        save_as_button.pack(pady=2)

        # TEXT WIDGET (NOT StringVar, NOT textvariable)
        self.text = tk.Text(self.root, width=200, height=100)
        self.text.pack(pady=16)

        # load saved text into widget
        self.text.insert(
            "1.0",
            self.config["Write"]["savestring"]
        )

        # start disabled
        self.text.config(state="disabled")

    def _load_config(self):
        """Load the saved text buffer from the shared config file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Back-compat: migrate old Tool Template key to Write.
                    if "Write" not in data and "Tool Template" in data:
                        data["Write"] = data.get("Tool Template", {"savestring": ""})
                    return data
            except json.JSONDecodeError:
                pass
        return self.default_config

    def _on_enable_entry(self):
        """Unlock the text widget so the user can edit its contents."""
        self.text.config(state="normal") #state normal to enable editing
        
        self.text.focus_set() #a function to focus the text widget when edit button is clicked

    def _on_save_entry(self):
        """Persist the current text buffer into the shared config file."""
        # READ from Text widget correctly
        text = self.text.get("1.0", "end-1c")

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        #write the data to config file
        data = {
            "Write": {
                "savestring": text
            }
        }

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4) 

        self.text.config(state="disabled") #state disabled to prevent editing after saving

    def _on_save_as_entry(self):
        """Export the current text buffer to a user-selected file."""
        text = self.text.get("1.0", "end-1c")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
                self._on_save_entry()
        except Exception as e:
            print(f"Error saving file: {e}")
            

def run():
    """Launch the Write tool."""
    root = tk.Tk()
    Write(root)
    root.mainloop()


if __name__ == "__main__":
    run()
