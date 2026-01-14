import os
import sys
import time
import zipfile
import logging
import requests
import subprocess
import shutil
from pathlib import Path

REPO = "PawelKawka/DayzOpenLauncher"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

def setup_logging(root_dir):
    log_file = root_dir / "updater.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def kill_process_by_name(name):
    try:
        if sys.platform != "win32":
            my_pid = os.getpid()
            pids_raw = subprocess.check_output(["pgrep", "-f", name]).decode().split()
            for pid_str in pids_raw:
                pid = int(pid_str)
                if pid != my_pid:
                    logging.info(f"Force closing process PID: {pid}")
                    try:
                        os.kill(pid, 9)
                    except OSError:
                        pass
    except subprocess.CalledProcessError:
        pass
    except Exception as e:
        logging.warning(f"Error closing processes: {e}")

def update():
    if getattr(sys, 'frozen', False):
        current_exe = Path(sys.executable)
        if current_exe.parent.name == "_internal":
            root_dir = current_exe.parent.parent
        else:
            root_dir = current_exe.parent
    else:
        root_dir = Path(__file__).parent.parent.parent
    
    setup_logging(root_dir)
    logging.info("Starting update process...")

    time.sleep(2)

    try:
        logging.info("Fetching latest release from GitHub...")
        response = requests.get(GITHUB_API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        version = data.get("tag_name", "unknown")

        assets = data.get("assets", [])
        download_url = next((a.get("browser_download_url") for a in assets if "linux.zip" in a.get("name", "").lower()), None)

        if not download_url:
            logging.error("Error: linux.zip not found in Release")
            return

        zip_path = root_dir / "update_package.zip"
        logging.info(f"Downloading version {version} from: {download_url}")
        
        with requests.get(download_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)

        logging.info("Installing...")
        temp_extract = root_dir / "temp_update_extract"
        if temp_extract.exists(): shutil.rmtree(temp_extract)
        temp_extract.mkdir()
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        source_content_dir = None
        for p in temp_extract.rglob("DayzOpenLauncher"):
            if p.is_file():
                source_content_dir = p.parent
                break
        
        if not source_content_dir:
            logging.error("Error: Binary not found in update package")
            return

        logging.info(f"Copying new files from {source_content_dir} to {root_dir}")
        
        for item in source_content_dir.iterdir():
            if item.name == "updater" or item.name == "updater.log" or item.name == "update_package.zip":
                continue 
                
            dest = root_dir / item.name
            try:
                if item.is_dir():
                    if dest.exists(): shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    if dest.exists(): dest.unlink()
                    shutil.copy2(item, dest)
            except Exception as e:
                logging.warning(f"Problem copying {item.name}: {e}. Continuing...")

        logging.info("Cleaning up temporary files...")
        zip_path.unlink(missing_ok=True)
        shutil.rmtree(temp_extract, ignore_errors=True)

        launcher_path = root_dir / "DayzOpenLauncher"
        if launcher_path.exists():
            try:
                os.chmod(launcher_path, 0o755)
            except: pass
            
            logging.info(f"Update to {version} successful")
            logging.info("You can now run it using command: dayzopenlauncher")
            sys.exit(0)
        else:
            logging.error("CRITICAL ERROR: Launcher binary not found after update")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Critical update error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    update()
