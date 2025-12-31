from pathlib import Path

# Target the specific project and file mentioned in the error
artifact_path = Path(r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts\70d66cee-e04e-4f28-897f-55e33c6973ac\code\frontend\app\page.tsx")

if artifact_path.exists():
    with open(artifact_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Check if first line is the bad header
    if lines and lines[0].strip().startswith("#"):
        print(f"Removing header from {artifact_path}: {lines[0].strip()}")
        new_content = "".join(lines[1:])
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Success.")
    else:
        print("No header found or file empty.")
else:
    print(f"File not found: {artifact_path}")
