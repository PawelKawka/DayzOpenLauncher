import os
import sys
import time

try:
    from steamworks import STEAMWORKS
    from steamworks.enums import EItemState
except ImportError:
    STEAMWORKS = None
    EItemState = None

class SteamHelper:
    def __init__(self):
        self.steam = None
        self.workshop = None
        self.initialized = False

    def init(self):
        if not STEAMWORKS:
            return False
            
        root_dir = os.getcwd()
        appid_path = os.path.join(root_dir, "steam_appid.txt")
        if not os.path.exists(appid_path):
            try:
                with open(appid_path, "w") as f:
                    f.write("221100")
            except:
                pass
        
        try:
            self.steam = STEAMWORKS()
            self.steam.initialize()
            self.workshop = self.steam.Workshop
            self.initialized = True
            return True
        except Exception as e:
            return False

    def is_mod_installed(self, mod_id):
        if not self.initialized: return False
        try:
            state = self.workshop.GetItemState(int(mod_id))
            val = state.value if hasattr(state, 'value') else state
            return (val & 4) == 4
        except:
            return False

    def is_subscribed(self, mod_id):
        if not self.initialized: return False
        try:
            state = self.workshop.GetItemState(int(mod_id))
            val = state.value if hasattr(state, 'value') else state
            return (val & 1) == 1
        except:
            return False

    def subscribe_mod(self, mod_id):
        if not self.initialized: return
        try:
            self.workshop.SubscribeItem(int(mod_id))
        except:
            pass

