import os
import shutil
import time

def cleanup():
    # Target folders
    try:
        if os.path.exists('apps/web'):
            print("Moving frontend...")
            shutil.move('apps/web', 'frontend')
    except Exception as e:
        print(f"Error moving frontend: {e}")

    try:
        if os.path.exists('apps/api'):
            print("Moving backend...")
            shutil.move('apps/api', 'backend')
    except Exception as e:
        print(f"Error moving backend: {e}")

    # Remove Node structure
    paths_to_delete = ['packages', 'apps', 'package.json', 'package-lock.json', 'turbo.json', 'render.yaml', 'node_modules']
    for path in paths_to_delete:
        if os.path.exists(path):
            try:
                print(f"Deleting {path}...")
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
            except Exception as e:
                print(f"Error deleting {path}: {e}")

if __name__ == "__main__":
    cleanup()
