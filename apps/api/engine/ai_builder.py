from typing import Dict, Any

class AIBuilder:
    async def build_project(self, project_id: str, description: str) -> Dict[str, Any]:
        return {
            "projectId": project_id,
            "files": [
                {"path": "README.md", "content": f"# Project {project_id}\n\nGenerated for: {description}"}
            ],
            "stats": {"fileCount": 1}
        }
