import asyncio
import sys
import os
from pathlib import Path

# Add the apps/api directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.ai_builder import AIBuilder
from engine.project_manager import ProjectManager, ARTIFACTS_DIR

async def force_rebuild(project_id: str):
    pm = ProjectManager()
    builder = AIBuilder()
    
    project = await pm.get_project(project_id)
    if not project:
        print(f"Project {project_id} not found")
        return
    
    print(f"--- FORCE REBUILD STARTED ---")
    print(f"Project: {project.name} ({project_id})")
    
    # Update status to CODING
    await pm.update_project_status(project_id, "CODING")
    
    try:
        print("Generating code structure (Tri-Source Strategy)...")
        # Reuse existing build_project logic
        build_result = await builder.build_project(project_id, project.description)
        
        print("Persisting files to disk...")
        await pm.save_build_result(project_id, build_result)
        
        await pm.update_project_status(project_id, "COMPLETED")
        print("\nSUCCESS: Codebase regenerated and persisted to disk!")
        print(f"Artifacts path: {ARTIFACTS_DIR / project_id / 'code'}")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        await pm.update_project_status(project_id, "DESIGNED")

if __name__ == "__main__":
    # Default ID for current session if none provided
    default_id = "ac2e93f6-b5d0-47b6-840b-6e0571518ac2"
    project_id = sys.argv[1] if len(sys.argv) > 1 else default_id
    
    asyncio.run(force_rebuild(project_id))
