import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    from start import DayZLauncherTUI
    
    tui = DayZLauncherTUI()
    tui.run()