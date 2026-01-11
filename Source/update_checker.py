import threading
import time
import requests
import webbrowser
from prompt_toolkit.filters import Condition
from constants import VERSION

class UpdateChecker:
    def __init__(self, tui_app):
        self.tui = tui_app

    def start_check(self):
        def _check():
            try:
                time.sleep(3)
                
                response = requests.get("https://api.github.com/repos/PawelKawka/DayzOpenLauncher/releases/latest", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_tag = data.get("tag_name", "")
                    latest_ver = latest_tag.lstrip('v').split('-')[0].split(' ')[0] 
                    
                    try:
                        l_parts = [int(x) for x in latest_ver.split('.')]
                        c_parts = [int(x) for x in VERSION.split('.')]
                        is_new = l_parts > c_parts
                    except:
                        is_new = latest_ver != VERSION

                    if is_new:
                        self.tui.latest_update_info = {
                            "tag": latest_tag,
                            "body": data.get("body", ""),
                            "url": data.get("html_url", "https://github.com/PawelKawka/DayzOpenLauncher/releases")
                        }
                        
                        # switch to updates tab
                        self.tui.switch_tab("UPDATES")
                        
                        if hasattr(self.tui, 'app'):
                            self.tui.app.invalidate()
            except Exception:
                pass
                
        threading.Thread(target=_check, daemon=True).start()
