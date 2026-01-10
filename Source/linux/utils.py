import os
import re

def get_steam_path():
    paths = [
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.steam/debian-installation"),
        os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/Steam"), # flatpak
        os.path.expanduser("~/snap/steam/common/.local/share/Steam") # snap
    ]
    for p in paths:
        if p and os.path.exists(p):
            if os.path.exists(os.path.join(p, "steamapps")):
                return p
    return None

def get_dayz_path(steam_path):
    if not steam_path:
        return None
    
    default_path = os.path.join(steam_path, "steamapps", "common", "DayZ")
    if os.path.exists(default_path):
        return default_path
    
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(vdf_path):
        try:
            with open(vdf_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # find all path loc
            paths = re.findall(r'"path"\s+"([^"]+)"', content)
            for p in paths:
                dayz_candidate = os.path.join(p, "steamapps", "common", "DayZ")
                if os.path.exists(dayz_candidate):
                    return dayz_candidate
        except:
            pass
            
    return None
