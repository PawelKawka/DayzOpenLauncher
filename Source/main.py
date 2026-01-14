import sys
import os
import requests
import subprocess
import platform
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "launcher.log"),
        logging.StreamHandler()
    ]
)

if getattr(sys, 'frozen', False):
    root_dir = os.path.dirname(sys.executable)
    internal_dir = os.path.join(root_dir, "_internal")
    if os.path.exists(internal_dir):
        sys.path.insert(0, internal_dir)
else:
    sys.path.insert(0, os.path.dirname(__file__))

from constants import VERSION

def start_update_process():
    logging.info("Initiating the update process...")
    try:
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
            updater_bin = base_dir / "_internal" / "updater"
            if not updater_bin.exists():
                updater_bin = base_dir / "updater"
            
            if platform.system() == "Linux":
                try:
                    os.chmod(updater_bin, 0o755)
                except:
                    pass
                os.execv(str(updater_bin), [str(updater_bin)])
            else:
                subprocess.Popen([str(updater_bin)], start_new_session=True, cwd=str(base_dir))
                sys.exit(0)
        else:
            base_dir = Path(__file__).parent
            updater_script = base_dir / "linux" / "updater.py"
            if platform.system() == "Linux":
                os.execv(sys.executable, [sys.executable, str(updater_script)])
            else:
                subprocess.Popen([sys.executable, str(updater_script)], start_new_session=True, cwd=str(base_dir))
                sys.exit(0)
        
        logging.info("Updater has been started. Closing the main application.")
    except Exception as e:
        logging.error(f"Failed to start the update process: {e}")

def check_for_updates():
    repo = "PawelKawka/DayzOpenLauncher"
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    try:
        logging.info("Checking for updates...")
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_tag = data.get("tag_name", "").lstrip('v')
        
        if latest_tag != VERSION:
            logging.info(f"New version available: {latest_tag}")
            return True, latest_tag
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while checking for updates: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while checking for updates: {e}")
    
    return False, None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "remove":
        print("--- DayzOpenLauncher removal ---")
        confirm = input("Are you sure you want to remove DayzOpenLauncher? (y/N): ")
        if confirm.lower() == 'y':
            try:
                home = Path.home()
                install_dir = home / ".local" / "share" / "DayzOpenLauncher"
                if install_dir.exists():
                    import shutil
                    shutil.rmtree(install_dir)
                    print(f"Removed files: {install_dir}")

                potential_links = [
                    home / ".local" / "bin" / "dayzopenlauncher",
                    Path("/usr/local/bin/dayzopenlauncher")
                ]
                for link in potential_links:
                    if link.exists():
                        if os.access(link, os.W_OK):
                            link.unlink()
                            print(f"Removed symlink: {link}")
                        else:
                            print(f"Requesting sudo to remove link: {link}")
                            os.system(f"sudo rm {link}")

                config_dir = home / ".config" / "DayzOpenLauncher"
                if config_dir.exists():
                    rem_conf = input("Do you want to remove config and favorites? (y/N): ")
                    if rem_conf.lower() == 'y':
                        import shutil
                        shutil.rmtree(config_dir)
                        print(f"Removed configuration: {config_dir}")

                print("Done")
            except Exception as e:
                print(f"Error during removal: {e}")
        sys.exit(0)

    from start import DayZLauncherTUI
    tui = DayZLauncherTUI()
    tui.run()
    
    if tui.run_update_on_exit:
        start_update_process()

