import tkinter as tk
import random
import string
import pyperclip

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class PasswordGenerator:
    """Password generator tool."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("420x280")
        self.root.resizable(True, True)
        apply_app_icon(self.root)
        self.img = tk.PhotoImage(file="assets/copy.png")
        self.length = 16
        self.random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=0))
        self.build_ui()
        


    def build_ui(self):
        self.length_entry = tk.Entry(self.root)
        self.length_entry.pack(pady=16)
        self.length_visual_label = tk.Label(self.root, text=f"Length: {self.length}")
        self.length_visual_label.pack(pady=16)
        self.password_label = tk.Label(self.root, text=f"password: {self.random_string}")
        self.password_label.pack(pady=5)
        self.copybttn = tk.Button(self.root, image=self.img, command=self._copy_to_clipboard)
        self.copybttn.pack(pady=16)
        generatebttn = tk.Button(self.root, text="generate", command=self.on_generate)
        generatebttn.pack(pady=16)
        self.length_entry.bind("<KeyRelease>", self._on_entry_change)
       

    def _copy_to_clipboard(self):
        pyperclip.copy(self.random_string)

    def _on_entry_change(self, event):
        try:
            self.length = int(self.length_entry.get())
            
            self.length_visual_label.config(text=f"Length: {self.length}")
            
        except ValueError:
            self.length = 16
            self.length_visual_label.config(text=f"cant be empty. Length: {self.length}")
            

    def on_generate(self):
        self.random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=self.length))
        self.password_label.config(text=f"password: {self.random_string}")
        
       
        
def run():
    root = tk.Tk()
    PasswordGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    run()
