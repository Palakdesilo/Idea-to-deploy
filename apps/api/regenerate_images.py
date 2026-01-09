
import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine.ai_designer import AIDesigner, ARTIFACTS_DIR
import inspect
from engine.llm_service import LLMService
print(f"LLMService loaded from: {inspect.getfile(LLMService)}")


# Force load Env
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

# Configure Logging
logging.basicConfig(level=logging.INFO)

async def regenerate(project_id: str):
    print(f"--- Regenerating Images for {project_id} ---")
    
    designer = AIDesigner()
    
    # 1. Load existing Wireframe JSONs
    wf_json_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "json"
    if not wf_json_dir.exists():
        print(f"ERROR: No wireframe JSONs found at {wf_json_dir}")
        return

    wireframes = []
    for json_file in wf_json_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Derive screen name from filename or data
            screen_name = json_file.stem.replace("_", " ").title()
            
            # Inject screen_name if missing (needed by generate_ai_renders)
            if "screen_name" not in data:
                data["screen_name"] = screen_name
                
            wireframes.append(data)
            print(f"Loaded wireframe: {screen_name}")
        except Exception as e:
            print(f"Failed to load {json_file}: {e}")

    if not wireframes:
        print("No valid wireframes found to process.")
        return

    # 2. Call generate_ai_renders
    # We need the 'idea_description' for the prompt. Retrieve it from project data or just use a generic one if missing.
    # Ideally getting it from docs.json or projects.json would be best, but for now let's try to fetch it from the ProjectManager if possible, 
    # or just simple read.
    
    try:
        from engine.project_manager import ProjectManager
        pm = ProjectManager()
        project = await pm.get_project(project_id)
        description = project.description if project else "A generic web application."
    except Exception:
        description = "A modern web application."

    print(f"Using Description: {description}")

    # 3. RUN GENERATION
    await designer.generate_ai_renders(project_id, wireframes, description)
    print("--- Regeneration Complete ---")

if __name__ == "__main__":
    # PROJECT ID is hardcoded based on user request
    PID = "ac2e93f6-b5d0-47b6-840b-6e0571518ac2"
    
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(regenerate(PID))
    except Exception as e:
        print(f"CRITIAL SCRIPT ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
