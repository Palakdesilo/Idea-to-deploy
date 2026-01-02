
import os
import json
from pathlib import Path

output_file = Path("verification_output.txt")
with open(output_file, "w") as out:
    try:
        # Target project ID from previous observation
        project_id = "fa63b2f3-85e8-4111-b6f9-d346d99360a5"
        base_dir = Path("apps/api/data/artifacts") / project_id / "docs"

        out.write(f"Checking directory: {base_dir.absolute()}\n")

        if not base_dir.exists():
            out.write("Directory does not exist!\n")
            # Try finding the latest project
            artifacts_root = Path("apps/api/data/artifacts")
            if artifacts_root.exists():
                projects = list(artifacts_root.iterdir())
                if projects:
                    latest_project = max(projects, key=os.path.getmtime)
                    out.write(f"Switching to latest project: {latest_project.name}\n")
                    base_dir = latest_project / "docs"

        files_to_check = [
            "screen_inventory.json",
            "ui_contracts.json",
            "wireframes.json",
            "ui_design.json",
            "figma_layout.json"
        ]

        if base_dir.exists():
            for filename in files_to_check:
                file_path = base_dir / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    out.write(f"\nFile: {filename}\n")
                    out.write(f"Size: {size} bytes\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            out.write(f"Snippet: {content[:100]}...\n")
                            if size < 500:
                                 out.write(f"Full Content: {content}\n")
                            
                            if filename.endswith('.json'):
                                try:
                                    json_content = json.loads(content)
                                    if isinstance(json_content, list):
                                        out.write(f"JSON Structure: List with {len(json_content)} items\n")
                                    elif isinstance(json_content, dict):
                                        keys = list(json_content.keys())
                                        out.write(f"JSON Structure: Dict with keys {keys}\n")
                                except json.JSONDecodeError:
                                    out.write("INVALID JSON\n")
                    except Exception as e:
                        out.write(f"Error reading: {e}\n")
                else:
                    out.write(f"\nFile: {filename} - MISSING\n")
        else:
            out.write(f"Docs directory not found at {base_dir}\n")
    except Exception as e:
        out.write(f"CRITICAL ERROR: {e}\n")
