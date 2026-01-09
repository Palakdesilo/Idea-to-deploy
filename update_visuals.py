
import json
import os
from pathlib import Path

PROJECT_ID = "ac2e93f6-b5d0-47b6-840b-6e0571518ac2"
ARTIFACTS_DIR = Path(r"D:\Palak\Idea-to-deploy\data\artifacts")
PROJECT_DIR = ARTIFACTS_DIR / PROJECT_ID
VISUALS_FILE = PROJECT_DIR / "visuals.json"
UI_DIR = PROJECT_DIR / "ui"

def update_visuals():
    if not VISUALS_FILE.exists():
        print(f"Visuals file not found: {VISUALS_FILE}")
        return

    with open(VISUALS_FILE, 'r') as f:
        visuals = json.load(f)

    updated_count = 0
    for visual in visuals:
        # Check current image path to derive filename
        # imageUrl: "/api/projects/.../wireframes/name.png"
        current_url = visual.get("imageUrl", "")
        if not current_url:
            continue
            
        filename = current_url.split('/')[-1] # e.g., category_page.png
        stem = os.path.splitext(filename)[0] # category_page
        
        # Construct expected high-fi filename
        highfi_filename = f"{stem}_highfi.png"
        highfi_path = UI_DIR / highfi_filename
        
        if highfi_path.exists():
            print(f"Found High-Fi for {visual['title']}: {highfi_filename}")
            
            # Update Visual
            visual['imageUrl'] = f"/api/projects/{PROJECT_ID}/ui/{highfi_filename}"
            visual['localPath'] = str(highfi_path)
            visual['type'] = "ui_design"
            
            if "(Wireframe)" in visual['title']:
                visual['title'] = visual['title'].replace("(Wireframe)", "(High-Fidelity UI)")
                
            updated_count += 1
        else:
            print(f"No High-Fi found for {visual['title']} (Checked {highfi_path})")

    if updated_count > 0:
        with open(VISUALS_FILE, 'w') as f:
            json.dump(visuals, f, indent=2)
        print(f"Successfully updated {updated_count} visuals to High-Fi.")
    else:
        print("No changes made.")

if __name__ == "__main__":
    update_visuals()
