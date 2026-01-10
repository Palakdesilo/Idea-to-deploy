import asyncio
from engine.project_manager import ProjectManager
from pathlib import Path

async def test_save():
    pm = ProjectManager()
    project_id = "ac2e93f6-b5d0-47b6-840b-6e0571518ac2"
    test_result = {
        "projectId": project_id,
        "files": [
            {"path": "apps/web/app/test_build.txt", "content": "Build System Test - " + str(asyncio.get_event_loop().time())}
        ]
    }
    print("Testing save_build_result...")
    await pm.save_build_result(project_id, test_result)
    print("Test build file should be created.")

if __name__ == "__main__":
    asyncio.run(test_save())
