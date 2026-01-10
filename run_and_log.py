import subprocess
import os

def run():
    print("Starting process...")
    cmd = ["python", "apps/api/rebuild.py", "ac2e93f6-b5d0-47b6-840b-6e0571518ac2"]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        with open("rebuild_final_log.txt", "w") as f:
            f.write(output)
        print("Success! Log written.")
    except subprocess.CalledProcessError as e:
        with open("rebuild_final_log.txt", "w") as f:
            f.write(f"FAILED with exit code {e.returncode}\n")
            f.write(e.output)
        print("Failed. Log written.")
    except Exception as e:
        with open("rebuild_final_log.txt", "w") as f:
            f.write(f"CRITICAL ERROR: {str(e)}\n")
        print("Critical error. Log written.")

if __name__ == "__main__":
    run()
