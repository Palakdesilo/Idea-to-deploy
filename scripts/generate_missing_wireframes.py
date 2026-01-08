import asyncio
import os
import sys
import json
import re
import uuid
import aiohttp
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_DIR = PROJECT_ROOT / "apps" / "api"

# Redirect print to a log file
log_file = open("scripts/gen_log.txt", "w", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

sys.path.append(str(API_DIR))

# Load Env
env_path = API_DIR / ".env"


if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"Loaded env from {env_path}", flush=True)
else:
    print(f"Warning: .env not found at {env_path}", flush=True)

try:
    from engine.project_manager import ProjectManager, ARTIFACTS_DIR
    from engine.llm_service import LLMService
except Exception as e:
    print(f"Import Error: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

async def generate_missing_wireframes():
    print("--- Starting Wireframe Backfill ---", flush=True)
    
    try:
        pm = ProjectManager()
        llm = LLMService()
        
        projects = await pm.get_all_projects()
        print(f"Found {len(projects)} projects.", flush=True)
    
    async with aiohttp.ClientSession() as session:
        for project in projects:
            print(f"\nProcessing Project: {project.name} ({project.id})")
            
            # 1. Get Screen List from Docs
            docs = await pm.get_docs(project.id)
            screen_doc = next((d for d in docs if "screen" in d.title.lower() or "page list" in d.title.lower()), None)
            
            if not screen_doc:
                print("  No screen list document found. Skipping.")
                continue
                
            # 2. Parse Screens (Reusing logic from AIDesigner)
            content = screen_doc.content
            
            # Extract Branding
            branding_context = "Professional UI style matching the project idea."
            try:
                branding_match = re.search(r'(?:###|\*\*|)\s*(?:Branding|Color Palette|Design System)(?:.*?)(\n.*?)(\n###|\n\*\*|$)', content, re.IGNORECASE | re.DOTALL)
                if branding_match:
                    branding_context = branding_match.group(1).strip()[:300]
            except:
                pass

            # Parse Screens
            screens = []
            current_screen = None
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                # Regex for "1. Title"
                match = re.match(r'^(\d+)\.\s+(?:\*\*)?([^\*:\-\n]+)(?:\*\*)?(?:\s*[:\-]\s*(.+))?$', line)
                if match:
                    title = match.group(2).strip()
                    initial_desc = match.group(3).strip() if match.group(3) else ""
                    if len(title) < 50 and "page" not in title.lower() and "list" in title.lower(): 
                        current_screen = None
                        continue
                    current_screen = {"title": title, "desc": initial_desc}
                    screens.append(current_screen)
                elif current_screen and (line.startswith('-') or line.startswith('*')):
                     clean_line = line.lstrip("-* ").strip()
                     current_screen["desc"] += f"; {clean_line}"

            if not screens:
                print("  No screens parsed from document.")
                continue

            print(f"  Parsed {len(screens)} screens from doc.")

            # 3. Check Existing Visuals
            existing_visuals = await pm.get_visuals(project.id)
            existing_titles = {v['title'].lower() for v in existing_visuals}
            
            visuals_dir = ARTIFACTS_DIR / project.id / "visuals"
            visuals_dir.mkdir(parents=True, exist_ok=True)
            
            # 4. Generate Missing
            new_visuals = []
            
            # Limit to first 8 screens as per original logic, but check which ones are missing
            screens_to_check = screens[:8]
            
            for screen in screens_to_check:
                if screen['title'].lower() in existing_titles:
                    print(f"  Skipping '{screen['title']}' (already exists)")
                    continue
                
                print(f"  > Generating wireframe for: {screen['title']}")
                
                image_prompt = (
                    f"Professional High-Fidelity UI Wireframe for a website screen named '{screen['title']}'. "
                    f"Context: {screen['desc']}. "
                    f"Style: Clean, Grayscale, Blueprint, Minimalist, Modern UI Layout. "
                    f"Key Elements: Sidebar, Navigation, Cards, Data Grid, Dashboard widgets (if applicable). "
                    f"Branding: {branding_context}. "
                    f"Visuals: Flat design, thin lines, Helvetica font, no photos, no 3D effects, no shadows. "
                    f"Make it look like a Figma or Sketch design mockup."
                )
                
                image_url = await llm.generate_image(image_prompt)
                
                if image_url:
                    filename = f"{uuid.uuid4()}.png"
                    file_save_path = visuals_dir / filename
                    
                    try:
                        async with session.get(image_url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                with open(file_save_path, "wb") as f:
                                    f.write(data)
                                
                                new_visual_entry = {
                                    "id": str(uuid.uuid4()),
                                    "title": screen['title'],
                                    "screenName": screen['title'],
                                    "description": screen['desc'][:100] + "...",
                                    "imageUrl": f"/api/projects/{project.id}/visuals/{filename}",
                                    "localPath": str(file_save_path),
                                }
                                new_visuals.append(new_visual_entry)
                                print(f"    Saved {filename}")
                            else:
                                print(f"    Failed to download: {resp.status}")
                    except Exception as e:
                        print(f"    Error saving: {e}")
                else:
                    print("    LLM returned no image URL.")
            
            if new_visuals:
                all_visuals = existing_visuals + new_visuals
                await pm.save_visuals(project.id, all_visuals)
                print(f"  Updated visuals.json with {len(new_visuals)} new images.")
            else:
                print("  No new images generated.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(generate_missing_wireframes())
