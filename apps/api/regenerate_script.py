import asyncio
import sys
from pathlib import Path

# Add apps/api to path
sys.path.append(r"d:\Palak\Idea-to-deploy\apps\api")

from engine.ai_coder import AICoder
from engine.project_manager import ProjectManager

ARTIFACTS_DIR = Path(r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts")
PROJECT_ID = "a527e7fb-77e8-4e9f-b3d8-a332ebd2501a"

async def regenerate():
    print(f"Starting regeneration for {PROJECT_ID}...")
    
    # helper to get project data
    pm = ProjectManager(ARTIFACTS_DIR)
    project = await pm.get_project(PROJECT_ID)
    
    coder = AICoder()
    
    # We need to ensure we have the 'idea' and 'entities' etc.
    # AICoder.generate_code fetches what it needs from artifacts usually, 
    # but let's check the signature.
    # def generate_code(self, project_id: str): ...
    
    result = await coder.generate_code(PROJECT_ID)
    print("Generation complete!")
    print(f"Status: {result.get('status')}")
    print(f"Files generated: {len(result.get('files', []))}")

if __name__ == "__main__":
    asyncio.run(regenerate())
