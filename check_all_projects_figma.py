
import os
from pathlib import Path

artifacts_dir = Path(r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts")
required_files = ["figma_layout.json", "figma_nodes_output.json", "json_to_figma.json"]

print("--- Checking all projects for Figma artifacts ---")

if not artifacts_dir.exists():
    print("Artifacts directory not found.")
else:
    for project_dir in artifacts_dir.iterdir():
        if project_dir.is_dir():
            print(f"\nProject: {project_dir.name}")
            docs_dir = project_dir / "docs"
            if not docs_dir.exists():
                print("  [MISSING] 'docs' directory")
                continue
            
            all_present = True
            for filename in required_files:
                file_path = docs_dir / filename
                if file_path.exists():
                     size = file_path.stat().st_size
                     if size > 0:
                         print(f"  [OK] {filename} ({size} bytes)")
                     else:
                         print(f"  [EMPTY] {filename}")
                         all_present = False
                else:
                    print(f"  [MISSING] {filename}")
                    all_present = False
            
            if all_present:
                print("  >> ALL FIGMA FILES VALID")

print("\n--- Check complete ---")
