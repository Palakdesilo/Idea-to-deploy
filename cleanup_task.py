import shutil
import os
import time

LOG_FILE = "cleanup_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def copy_data():
    src = os.path.join("apps", "api", "data")
    dst = "data"
    if os.path.exists(src):
        log(f"Found source data at {src}")
        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)
            log(f"Successfully copied {src} to {dst}")
        except Exception as e:
            log(f"Error copying data: {e}")
    else:
        log(f"Source {src} does not exist, skipping copy.")

def delete_path(path):
    if os.path.exists(path):
        log(f"Deleting {path}...")
        try:
            shutil.rmtree(path, ignore_errors=True)
            if os.path.exists(path):
                 log(f"Failed to delete {path} (still exists)")
            else:
                 log(f"Successfully deleted {path}")
        except Exception as e:
            log(f"Error deleting {path}: {e}")
    else:
        log(f"{path} does not exist.")

if __name__ == "__main__":
    copy_data()
    delete_path(os.path.join("apps", "api"))
    delete_path(os.path.join("packages", "engine"))
    delete_path(os.path.join("packages", "types"))
    log("Cleanup complete.")
