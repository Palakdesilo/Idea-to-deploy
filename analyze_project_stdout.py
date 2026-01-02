
import json
from pathlib import Path
import sys

# Target project ID (using the one from before)
project_id = "fa63b2f3-85e8-4111-b6f9-d346d99360a5"
artifacts_dir = Path("apps/api/data/artifacts") / project_id
docs_dir = artifacts_dir / "docs"
docs_json_file = artifacts_dir / "docs.json"

print(f"Analyzing Project: {project_id}")

# 1. Verify docs.json content
if docs_json_file.exists():
    try:
        data = json.loads(docs_json_file.read_text(encoding='utf-8'))
        print(f"\n--- Core Docs ({len(data)} items) ---")
        for doc in data:
            title = doc.get('title', 'Untitled')
            category = doc.get('category', 'Unknown')
            content = doc.get('content', '')
            print(f"[{category}] {title}: {len(content)} chars")
    except Exception as e:
        print(f"Error reading docs.json: {e}")
else:
    print("\n! docs.json MISSING")

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
        
        print(f"\n--- Screen Inventory ({len(inventory_screens)} screens) ---")
        print(f"Screens: {', '.join(str(s) for s in inventory_screens)}")
    except Exception as e:
        print(f"Error reading screen_inventory.json: {e}")

if wireframes_file.exists():
    try:
        wf_data = json.loads(wireframes_file.read_text(encoding='utf-8'))
        if isinstance(wf_data, dict) and 'wireframes' in wf_data:
            wireframe_screens = [w.get('screen') for w in wf_data['wireframes']]
        
        print(f"\n--- Wireframes Generated ({len(wireframe_screens)} screens) ---")
        print(f"Screens: {', '.join(str(s) for s in wireframe_screens)}")
    except Exception as e:
        print(f"Error reading wireframes.json: {e}")

# 3. Check for Discrepancies
missing = [s for s in inventory_screens if s not in wireframe_screens]
if missing:
    print(f"\n!!! MISSING SCREENS (In Inventory but not Wireframes): {missing}")
else:
    print("\nAll inventory screens accounted for in wireframes.")
