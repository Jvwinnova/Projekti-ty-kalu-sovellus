import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.app.main import main

if __name__ == "__main__":
    if "--pong" in sys.argv:
        from src.app.tools import pong
        pong.main()
        try:
            pong.pygame.quit()
        except Exception:
            pass
    else:
        main()
