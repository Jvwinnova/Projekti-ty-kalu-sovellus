"""Basic four-function calculator with a button-based Tkinter UI."""

import tkinter as tk
from tkinter import ttk
import math

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class Calc:
    """Evaluate simple arithmetic expressions entered through calculator buttons."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("360x460")
        self.root.resizable(False, False)
        apply_app_icon(self.root)

        self.expression = ""
        self.display_var = tk.StringVar(value="")

        self._build_ui()
    def _build_ui(self):
        """Create the read-only display and calculator button grid."""
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Calculator", font=("Segoe UI", 16, "bold")).pack(pady=(0, 8))

        display = ttk.Entry(
            container,
            textvariable=self.display_var,
            font=("Segoe UI", 18),
            justify="right",
            state="readonly",
        )
        display.pack(fill=tk.X, pady=(0, 12))

        pad = ttk.Frame(container)
        pad.pack(fill=tk.BOTH, expand=True)

        # Row 0
        ttk.Button(pad, text="7", command=self.on_7).grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="8", command=self.on_8).grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="9", command=self.on_9).grid(row=0, column=2, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="/", command=self.on_divide).grid(row=0, column=3, padx=4, pady=4, sticky="nsew")
      

        # Row 1
        ttk.Button(pad, text="4", command=self.on_4).grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="5", command=self.on_5).grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="6", command=self.on_6).grid(row=1, column=2, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="*", command=self.on_multiply).grid(row=1, column=3, padx=4, pady=4, sticky="nsew")
       

        # Row 2
        ttk.Button(pad, text="1", command=self.on_1).grid(row=2, column=0, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="2", command=self.on_2).grid(row=2, column=1, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="3", command=self.on_3).grid(row=2, column=2, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="-", command=self.on_minus).grid(row=2, column=3, padx=4, pady=4, sticky="nsew")
       
        ttk.Button(pad, text="0", command=self.on_0).grid(row=3, column=0, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text=".", command=self.on_dot).grid(row=3, column=1, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="=", command=self.on_equals).grid(row=3, column=2, padx=4, pady=4, sticky="nsew")
        ttk.Button(pad, text="+", command=self.on_plus).grid(row=3, column=3, padx=4, pady=4, sticky="nsew")
       
        # Row 4
        ttk.Button(pad, text="C", command=self.on_clear).grid(row=4, column=0, columnspan=2, padx=4, pady=6, sticky="nsew")
        ttk.Button(pad, text="Back", command=self.on_back).grid(row=4, column=2, columnspan=2, padx=4, pady=6, sticky="nsew")

        for i in range(5):
            pad.columnconfigure(i, weight=1)
        for i in range(5):
            pad.rowconfigure(i, weight=1)

    def _append(self, value: str):
        """Append a digit or decimal text fragment to the current expression."""
        if self.expression == "0":
            self.expression = value
            self._sync_display()
        else:
            
            self.expression += value
            self._sync_display()

    def _append_operator(self, op: str):
        """Append or replace the trailing operator in the current expression."""
        if not self.expression:
            if op == "-":
                self.expression = "-"
                self._sync_display()
            return
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1] + op
        else:
            self.expression += op
        self._sync_display()

    def _sync_display(self):
        """Push the internal expression string to the on-screen display."""
        self.display_var.set(self.expression if self.expression else "")

    def _safe_eval(self, expr: str):
        """Evaluate a sanitized arithmetic expression with builtins disabled."""
        allowed = set("0123456789+-*/. ")
        if not expr or any(ch not in allowed for ch in expr):
            raise ValueError("Invalid expression")
        return eval(expr, {"__builtins__": {}}, {})

 

    # Digit handlers
    def on_0(self):
        self._append("0")

    def on_1(self):
        self._append("1")

    def on_2(self):
        self._append("2")

    def on_3(self):
        self._append("3")

    def on_4(self):
        self._append("4")

    def on_5(self):
        self._append("5")

    def on_6(self):
        self._append("6")

    def on_7(self):
        self._append("7")

    def on_8(self):
        self._append("8")

    def on_9(self):
        self._append("9")

    # Operator handlers
    def on_plus(self):
        self._append_operator("+")

    def on_minus(self):
        self._append_operator("-")

    def on_multiply(self):
        self._append_operator("*")

    def on_divide(self):
        self._append_operator("/")

    

   

    def on_dot(self):
        # Handle empty expression
        if self.expression == "":
            self.expression += "0."
            self._sync_display()
            return
        
        # If character is an operator, append "0." to start a new decimal number
        if self.expression[-1] in "+-*/":
            self.expression += "0."
            self._sync_display()
            return
        
        # Prevent multiple dots in the current number
        last_op = max(self.expression.rfind(op) for op in "+-*/")
        current = self.expression[last_op + 1 :]
        if "." in current:
            return
        self.expression += "."
        self._sync_display()

    def on_clear(self):
        self.expression = ""
        self._sync_display()

    def on_back(self):
        if self.expression:
            self.expression = self.expression[:-1]
            self._sync_display()

    def on_equals(self):
        if not self.expression:
            return
        expr = self.expression
        while expr and expr[-1] in "+-*/":
            expr = expr[:-1]
        if not expr:
            return
        try:
            result = self._safe_eval(expr)
        except Exception:
            self.display_var.set("Error")
            self.expression = ""
            return
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        self.expression = str(result)
        self._sync_display()


def run():
    """Launch the calculator window."""
    root = tk.Tk()
    Calc(root)
    root.mainloop()


if __name__ == "__main__":
    run()
