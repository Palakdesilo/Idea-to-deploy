
import json
from pathlib import Path
import os

files_to_check = [
    r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts\fa63b2f3-85e8-4111-b6f9-d346d99360a5\docs\figma_layout.json",
    r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts\fa63b2f3-85e8-4111-b6f9-d346d99360a5\docs\figma_nodes_output.json",
    r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts\fa63b2f3-85e8-4111-b6f9-d346d99360a5\docs\json_to_figma.json"
]

print("--- Verifying Figma Artifacts ---")

for file_path_str in files_to_check:
    path = Path(file_path_str)
    name = path.name
    
    print(f"\nChecking: {name}")
    
    if not path.exists():
        print(f"  [MISSING] File not found at {path}")
        continue
        
    size = path.stat().st_size
    print(f"  [EXISTS] Size: {size} bytes")
    
    if size == 0:
        print("  [EMPTY] File is empty")
        continue
        
    try:
        content = path.read_text(encoding='utf-8')
        data = json.loads(content)
        print("  [VALID JSON] Successfully parsed")
        
        # Specific structural checks
        if name == "figma_layout.json":
            # Expecting keys like "figma", "pages"
            if "figma" in data:
                print("  [STRUCTURE] Found 'figma' root key")
                pages = data["figma"].get("pages", [])
                print(f"  [CONTENT] Found {len(pages)} pages")
                if pages:
                    print(f"  [SAMPLE] First page: {pages[0].get('name')}")
                    frames = pages[0].get("frames", [])
                    print(f"  [SAMPLE] Frames in first page: {len(frames)}")
            else:
                print(f"  [WARNING] Unexpected structure. Keys: {list(data.keys())}")
                
        elif name == "figma_nodes_output.json":
            # Usually a large object or list of nodes
            if isinstance(data, dict):
                print(f"  [STRUCTURE] Root is Dict with {len(data)} keys")
                if "document" in data:
                     print("  [CONTENT] Found 'document' key (Standard Figma structure?)")
                elif "nodes" in data:
                     print(f"  [CONTENT] Found 'nodes' key with {len(data['nodes'])} items")
            elif isinstance(data, list):
                print(f"  [STRUCTURE] Root is List with {len(data)} items")
                if len(data) > 0:
                    print(f"  [SAMPLE] Item 0 keys: {list(data[0].keys())}")

        elif name == "json_to_figma.json":
             # This is usually the conversion mapping
            if isinstance(data, dict):
                 print(f"  [STRUCTURE] Root is Dict with {len(data)} keys")
            elif isinstance(data, list):
                 print(f"  [STRUCTURE] Root is List with {len(data)} items")
            
    except json.JSONDecodeError as e:
        print(f"  [INVALID JSON] Parse error: {e}")
    except Exception as e:
         print(f"  [ERROR] {e}")

print("\n--- Verification Complete ---")
