import uuid
from typing import List, Dict, Any

class AIDesigner:
    async def generate_visuals(self, project_id: str, description: str) -> List[Dict[str, Any]]:
        return [{
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "screenName": "Dashboard",
            "description": f"Design for {description[:30]}",
            "imageUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
            "promptUsed": "Premium UI",
            "purpose": "Main view",
            "roles": ["Admin"],
            "components": ["Charts"],
            "interactions": ["Click"],
            "states": ["Default"]
        }]
