"""Animated turtle-based random walk embedded inside a Tkinter window."""

import tkinter as tk
import random
import turtle

try:
    from src.app.window_icon import apply_app_icon
except ModuleNotFoundError:
    def apply_app_icon(window):
        return


class RandomWalk:
    """Infinite Random Walk inside ONE Tkinter window."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Random Walk")
        apply_app_icon(self.root)

        # Create canvas for turtle
        self.canvas = tk.Canvas(root, width=1200, height=1000)
        self.canvas.pack()

        # Attach turtle to canvas (IMPORTANT)
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.tracer(0)

        self.t = turtle.RawTurtle(self.screen)
        self.t.speed(0)

        # Position
        self.x = 0
        self.y = 0

        # Start walking
        self.walk_step()
    # function to perform one step of the random walk
    def walk_step(self):
        
       
        step = random.randint(1, 4)
        # according to the random value move in one of the four directions
        if step == 1:
            self.x += 1
        elif step == 2:
            self.y += 1
        elif step == 3:
            self.x -= 1
        else:
            self.y -= 1
        
        self.t.goto(self.x * 5, self.y * 5) # scale up the position for better visibility
        self.screen.update() # update the canvas to show the new position

        # Loop
        self.root.after(50, self.walk_step)


def run():
    """Launch the Random Walk tool."""
    root = tk.Tk()
    RandomWalk(root)
    root.mainloop()


if __name__ == "__main__":
    run()
