import uuid
from typing import List, Dict, Any

class AIDesigner:
    async def generate_visuals(self, project_id: str, description: str) -> List[Dict[str, Any]]:
        return [{"id": str(uuid.uuid4()), "projectId": project_id, "screenName": "Dashboard", "imageUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71"}]

class AIBuilder:
    async def build_project(self, project_id: str, description: str) -> Dict[str, Any]:
        return {"projectId": project_id, "files": [{"path": "README.md", "content": "# Generated"}]}

REQUIREMENT_PROMPT = "Create requirement for {idea}"
PLANNING_PROMPT = "Create plan for {idea}"
ARCHITECTURE_PROMPT = "Create arch for {idea}"
UI_UX_PROMPT = "Create UI for {idea}"
