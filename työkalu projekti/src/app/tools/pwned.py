import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import requests

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


def check_password(password: str, timeout_s: int = 10) -> int:
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(
        url,
        headers={"User-Agent": "pwned-password-check/1.0"},
        timeout=timeout_s,
    )
    res.raise_for_status()

    for line in res.text.splitlines():
        h, count = line.split(":")
        if h == suffix:
            return int(count)

    return 0


class PwnedPasswordChecker:
    """Check if a password appears in the Pwned Passwords dataset."""

    SOURCE_URL = "https://haveibeenpwned.com/Passwords"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pwned Passwords")
        self.root.geometry("520x300")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        self._checking = False
        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Pwned Passwords",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 6))

        ttk.Label(
            container,
            text=(
                "Your password is never sent in full. The check uses a "
                "k-anonymity range query."
                
            ),
            wraplength=470,
        ).pack(pady=(0, 12))

        entry_row = ttk.Frame(container)
        entry_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(entry_row, text="Password:").pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            entry_row,
            textvariable=self.password_var,
            show="*",
            width=36,
        )
        self.password_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        self.password_entry.bind("<Return>", self._on_check)

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            entry_row,
            text="Show",
            variable=self.show_var,
            command=self._toggle_show,
        ).pack(side=tk.LEFT, padx=(8, 0))

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(0, 10))

        self.check_button = ttk.Button(actions, text="Check", command=self._on_check)
        self.check_button.pack(side=tk.LEFT)

        ttk.Button(
            actions,
            text="Clear",
            command=self._clear,
        ).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(
            actions,
            text="Info",
            command=self._show_info,
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="Enter a password to check.")
        self.status_label = ttk.Label(container, textvariable=self.status_var, wraplength=470)
        self.status_label.pack(pady=(0, 6))

    def _toggle_show(self):
        self.password_entry.configure(show="" if self.show_var.get() else "*")

    def _copy_link(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.SOURCE_URL)
            self.status_var.set("Website copied to clipboard.")
        except Exception:
            self.status_var.set("Failed to copy website.")

    def _clear(self):
        if self._checking:
            return
        self.password_var.set("")
        self.status_var.set("Enter a password to check.")
        self.password_entry.focus_set()

    def _show_info(self):
        info = tk.Toplevel(self.root)
        info.title("Pwned Passwords Info")
        info.resizable(False, False)
        apply_app_icon(info)
        info.transient(self.root)
        info.grab_set()

        container = ttk.Frame(info, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Pwned Passwords",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=(0, 6))

        ttk.Label(
            container,
            text=(
                "Uses the Have I Been Pwned, Pwned Passwords API with "
                "k-anonymity."
            ),
            wraplength=420,
        ).pack(pady=(0, 10))

        link_row = ttk.Frame(container)
        link_row.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(link_row, text="Website:").pack(side=tk.LEFT)
        self.info_link_var = tk.StringVar(value=self.SOURCE_URL)
        self.info_link_entry = ttk.Entry(
            link_row,
            textvariable=self.info_link_var,
            state="readonly",
            width=36,
        )
        self.info_link_entry.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        ttk.Button(link_row, text="Copy", command=self._copy_link).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(container, text="Close", command=info.destroy).pack(anchor=tk.E)

    def _on_check(self, event=None):
        if self._checking:
            return
        password = self.password_var.get()
        if not password:
            self.status_var.set("Enter a password to check.")
            return

        self._set_checking(True)
        self.status_var.set("Checking...")

        thread = threading.Thread(
            target=self._check_in_background,
            args=(password,),
            daemon=True,
        )
        thread.start()

    def _check_in_background(self, password: str):
        try:
            count = check_password(password)
            self.root.after(0, lambda: self._show_result(count))
        except requests.RequestException as exc:
            self.root.after(0, lambda: self._show_error(str(exc)))
        except Exception:
            self.root.after(0, lambda: self._show_error("Unexpected error."))

    def _show_result(self, count: int):
        if count:
            self.status_var.set(f"Found {count} times ❌.")
        else:
            self.status_var.set("Not found ✅.")
        self._set_checking(False)

    def _show_error(self, message: str):
        self.status_var.set(f"Check failed: {message}")
        self._set_checking(False)

    def _set_checking(self, checking: bool):
        self._checking = checking
        state = tk.DISABLED if checking else tk.NORMAL
        self.check_button.configure(state=state)
        self.password_entry.configure(state=state)


def run():
    root = tk.Tk()
    PwnedPasswordChecker(root)
    root.mainloop()


if __name__ == "__main__":
    run()
