"""Simple Mad Lib game window."""

import random
import re
import tkinter as tk
from tkinter import ttk

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class MadLib:
    """Interactive Mad Lib minigame."""

    STORIES = [
        """
        One day, a {animal} went to {place} to {base_verb}.
        Everyone thought it was very {adjective}.
        """,

        """
        Yesterday, {person_name} threw a {object} into the sky
        and accidentally hit a {animal}.
        """,

        """
        The king of {place} ordered everyone to eat
        {food} while dancing with a {object}.
        """,

        """
        {person_name} found a magical {object} that could {base_verb}.
        """,

        """
        In the {adjective} forest, a {animal} was {verb_ing}.
        """,

        """
        Last night, I walked into a spooky pizza shop run by a dracula named {person_name}.
        He was wearing a giant {clothing_item} and juggling {plural_noun}.
        """,

        """
        The {adjective} wizard named {person_name} cast a spell
        that turned the king into a {animal}.
        """,

        """
        In the {adjective} city of {place}, a {animal} was elected mayor
        and promised to {base_verb} every day.
        """,

        """
        The {adjective} superhero named {person_name}
        had the power to {base_verb} and always wore a {clothing_item}.
        """,

        """
        At the {adjective} zoo, a {animal} named {person_name}
        escaped and started {verb_ing} with the visitors.
        """,

        """
        The {adjective} pirate named {person_name}
        sailed the seas in search of a legendary {object}
        that could {base_verb}.
        """,

        """
        A {adjective} scientist found a {object} that could cure all diseases,
        but {person_name} {verb_past} and accidentally created
        a {animal} that could talk.
        """,

        """
        {person_name} {verb_past} with {second_person_name},
        then they {second_verb_past} and became really {adjective} friends.
        """,

        """
        {person_name} {verb_past} a {object}
        and discovered it was a portal to a {adjective} world
        filled with {plural_noun}.
        """,

        """
        A {object} transported me to the year 3000, where everyone communicated through {plural_noun} and ate only {plural_food}.
        """,

        """
        The {adjective} chef named {person_name} created a new dish
        that combined {food} and {food}, and it became an instant hit.
        """,

          """
        The {adjective} detective named {person_name} solved the mystery of the missing {object} by {verb_ing} with a {animal}.
        """,
    ]
        

    

      
    

    

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mad Lib")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        apply_app_icon(self.root)

        self.entries = {}

        self.story_template = random.choice(self.STORIES)

        self._build_ui()

    def _build_ui(self):
        """Build the main UI."""

        container = ttk.Frame(self.root, padding=16,)
        
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Mad Lib",
            font=("Segoe UI", 18, "bold"),
        ).pack(pady=(0, 10))

        ttk.Label(
            container,
            text="Fill in the words below, then generate your story.",
            wraplength=380,
            justify="center",
        ).pack(pady=(0, 20))

        # Frame that holds all dynamic input fields
        self.form_frame = ttk.Frame(container)
        self.form_frame.pack(fill=tk.X)

        # Build initial fields
        self.build_fields()

        ttk.Button(
            container,
            text="New Story",
            command=self.new_story,
        ).pack(pady=(10, 0))

        self.generatestory_btn = ttk.Button(
            container,
            text="Generate Story",
            command=self.generate_story,
            state="normal"
        )
        self.generatestory_btn.pack(pady=(10, 20))

        self.result_text = tk.Text(
            container,
            height=10,
            wrap="word",
            font=("Segoe UI", 10),
            state="disabled"
        )

        self.result_text.pack(fill=tk.BOTH, expand=True)

    def build_fields(self):
        """Build entry fields for the current story."""

        # Remove old widgets
        for widget in self.form_frame.winfo_children():
            widget.destroy()

        self.entries.clear()

        # Find placeholders automatically
        fields = re.findall(r"\{(.*?)\}", self.story_template)

        # Create fields dynamically
        for field in fields:
            ttk.Label(
                self.form_frame,
                text=f"{field.capitalize()}:"
            ).pack(anchor="w", pady=(6, 0))

            entry = ttk.Entry(self.form_frame)
            entry.pack(fill=tk.X, pady=(0, 4))

            self.entries[field] = entry

    def generate_story(self):
        self.generatestory_btn.config(state="disabled")
        """Generate the completed Mad Lib story."""
    
        self.result_text.config(state="normal")
        answers = {
            field: entry.get() or ""
            for field, entry in self.entries.items()
        }

        final_story = self.story_template.format(**answers)

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, final_story.strip())
        self.result_text.config(state="disabled")
    def new_story(self):
        self.result_text.config(state="normal")
        self.generatestory_btn.config(state="normal")
        """Load a new random story."""

        # Pick a different story if possible
        available = [
            story for story in self.STORIES
            if story != self.story_template
        ]

        if available:
            self.story_template = random.choice(available)

        # Rebuild fields
        self.build_fields()

        # Clear old generated story
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")


def run():
    """Launch the Mad Lib tool."""

    root = tk.Tk()
    MadLib(root)
    root.mainloop()


if __name__ == "__main__":
    run()