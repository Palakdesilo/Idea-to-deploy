
import json
import shutil
from pathlib import Path

# Explicit paths
source_inv = Path(r"apps/api/data/artifacts/fa63b2f3-85e8-4111-b6f9-d346d99360a5/docs/screen_inventory.json")
source_wire = Path(r"apps/api/data/artifacts/fa63b2f3-85e8-4111-b6f9-d346d99360a5/docs/wireframes.json")

dest_file = Path("debug_dump.txt")

with open(dest_file, "w") as out:
    if source_inv.exists():
        out.write("--- INVENTORY ---\n")
        out.write(source_inv.read_text(encoding="utf-8"))
        out.write("\n\n")
    else:
        out.write("INVENTORY MISSING\n")

    if source_wire.exists():
        out.write("--- WIREFRAMES ---\n")
        out.write(source_wire.read_text(encoding="utf-8"))
        out.write("\n\n")
    else:
        out.write("WIREFRAMES MISSING\n")

print("Done")
