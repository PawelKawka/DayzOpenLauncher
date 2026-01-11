import sys
import os

if getattr(sys, 'frozen', False):
    root_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(root_dir, "_internal")
    if os.path.exists(internal_dir):
        sys.path.insert(0, internal_dir)
else:
    sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    from start import DayZLauncherTUI
    
    tui = DayZLauncherTUI()
    tui.run()