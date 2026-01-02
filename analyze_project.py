
import json
from pathlib import Path

# Target project ID (using the one from before)
project_id = "fa63b2f3-85e8-4111-b6f9-d346d99360a5"
artifacts_dir = Path("apps/api/data/artifacts") / project_id
docs_dir = artifacts_dir / "docs"
docs_json_file = artifacts_dir / "docs.json"

output_file = Path("analysis_output_direct.txt")
with open(output_file, "w") as out:
    out.write(f"Analyzing Project: {project_id}\n")

    # 1. Verify docs.json content
    if docs_json_file.exists():
        try:
            data = json.loads(docs_json_file.read_text(encoding='utf-8'))
            out.write(f"\n--- Core Docs ({len(data)} items) ---\n")
            for doc in data:
                title = doc.get('title', 'Untitled')
                category = doc.get('category', 'Unknown')
                content = doc.get('content', '')
                out.write(f"[{category}] {title}: {len(content)} chars\n")
                if len(content) < 50:
                    out.write(f"   WARNING: Content seems too short: '{content}'\n")
        except Exception as e:
            out.write(f"Error reading docs.json: {e}\n")
    else:
        out.write("\n! docs.json MISSING\n")

    # 2. Compare Screen Inventory vs Wireframes
    inventory_file = docs_dir / "screen_inventory.json"
    wireframes_file = docs_dir / "wireframes.json"

    inventory_screens = []
    wireframe_screens = []

    if inventory_file.exists():
        try:
            inv_data = json.loads(inventory_file.read_text(encoding='utf-8'))
            if isinstance(inv_data, dict) and 'screens' in inv_data:
                inventory_screens = [s.get('name') if isinstance(s, dict) else s for s in inv_data['screens']]
            elif isinstance(inv_data, dict) and 'screen_inventory' in inv_data:
                 inventory_screens = [s.get('name') if isinstance(s, dict) else s for s in inv_data['screen_inventory']]
            elif isinstance(inv_data, list):
                inventory_screens = [s.get('name') if isinstance(s, dict) else s for s in inv_data]
            
            out.write(f"\n--- Screen Inventory ({len(inventory_screens)} screens) ---\n")
            out.write(f"Screens: {', '.join(str(s) for s in inventory_screens)}\n")
        except Exception as e:
            out.write(f"Error reading screen_inventory.json: {e}\n")

    if wireframes_file.exists():
        try:
            wf_data = json.loads(wireframes_file.read_text(encoding='utf-8'))
            if isinstance(wf_data, dict) and 'wireframes' in wf_data:
                wireframe_screens = [w.get('screen') for w in wf_data['wireframes']]
            
            out.write(f"\n--- Wireframes Generated ({len(wireframe_screens)} screens) ---\n")
            out.write(f"Screens: {', '.join(str(s) for s in wireframe_screens)}\n")
        except Exception as e:
            out.write(f"Error reading wireframes.json: {e}\n")

    # 3. Check for Discrepancies
    missing = [s for s in inventory_screens if s not in wireframe_screens]
    extra = [s for s in wireframe_screens if s not in inventory_screens]

    if missing:
        out.write(f"\n!!! MISSING SCREENS (In Inventory but not Wireframes): {missing}\n")
    else:
        out.write("\nAll inventory screens accounted for in wireframes.\n")

    if extra:
        out.write(f"Note: Extra screens in wireframes: {extra}\n")
