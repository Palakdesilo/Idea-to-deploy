import os
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Any

# Add parent directory to sys.path to find models
sys.path.append(str(Path(__file__).parent.parent))

from models import Project, GeneratedDoc, ProjectStatus

def find_data_dir():
    # Use root data directory
    data_dir_env = os.getenv("DATA_DIR")
    if data_dir_env:
        return Path(data_dir_env)
    
    # Try current directory or parent (if running from apps/api-py)
    cwd = Path.cwd()
    if (cwd / "main.py").exists() and (cwd.parent.parent / "package.json").exists():
        return cwd.parent.parent / "data"
    
    return cwd / "data"

DATA_DIR = find_data_dir()
PROJECTS_FILE = DATA_DIR / "projects.json"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

class ProjectManager:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        if not PROJECTS_FILE.exists():
            with open(PROJECTS_FILE, 'w') as f:
                json.dump([], f)

    def _serialize_datetime(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    async def create_project(self, name: str, description: str) -> Project:
        projects = await self.get_all_projects()
        new_project = Project(
            name=name,
            description=description
        )
        projects.append(new_project)
        await self._save_projects(projects)
        
        project_dir = ARTIFACTS_DIR / new_project.id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        return new_project

    async def get_all_projects(self) -> List[Project]:
        if not PROJECTS_FILE.exists():
            return []
        with open(PROJECTS_FILE, 'r') as f:
            data = json.load(f)
            return [Project(**p) for p in data]

    async def get_project(self, id: str) -> Optional[Project]:
        projects = await self.get_all_projects()
        for p in projects:
            if p.id == id:
                return p
        return None

    async def update_project_status(self, id: str, status: ProjectStatus):
        projects = await self.get_all_projects()
        for p in projects:
            if p.id == id:
                p.status = status
                p.metrics.lastUpdated = datetime.now()
                await self._save_projects(projects)
                break

    async def get_docs(self, project_id: str) -> List[GeneratedDoc]:
        docs_file = ARTIFACTS_DIR / project_id / "docs.json"
        if not docs_file.exists():
            return []
        with open(docs_file, 'r') as f:
            data = json.load(f)
            return [GeneratedDoc(**d) for d in data]

    async def save_doc(self, project_id: str, category: str, title: str, content: str) -> GeneratedDoc:
        doc = GeneratedDoc(
            projectId=project_id,
            category=category,
            title=title,
            content=content
        )
        
        docs_file = ARTIFACTS_DIR / project_id / "docs.json"
        docs = []
        if docs_file.exists():
            with open(docs_file, 'r') as f:
                docs_data = json.load(f)
                docs = [GeneratedDoc(**d) for d in docs_data]
                
        # Remove old doc of same category
        docs = [d for d in docs if d.category != category]
        docs.append(doc)
        
        with open(docs_file, 'w') as f:
            json.dump([d.dict() for d in docs], f, default=self._serialize_datetime, indent=2)
            
        return doc

    async def get_visuals(self, project_id: str) -> List[Any]:
        visuals_file = ARTIFACTS_DIR / project_id / "visuals.json"
        if not visuals_file.exists():
            return []
        with open(visuals_file, 'r') as f:
            return json.load(f)

    async def save_visuals(self, project_id: str, visuals: List[Any]):
        visuals_file = ARTIFACTS_DIR / project_id / "visuals.json"
        with open(visuals_file, 'w') as f:
            json.dump(visuals, f, default=self._serialize_datetime, indent=2)

    async def get_build_result(self, project_id: str) -> Optional[Any]:
        build_file = ARTIFACTS_DIR / project_id / "build.json"
        if not build_file.exists():
            return None
        with open(build_file, 'r') as f:
            return json.load(f)

    async def save_build_result(self, project_id: str, build_result: Any):
        build_file = ARTIFACTS_DIR / project_id / "build.json"
        with open(build_file, 'w') as f:
            json.dump(build_result, f, default=self._serialize_datetime, indent=2)

    async def update_file_content(self, project_id: str, file_path: str, content: str):
        result = await self.get_build_result(project_id)
        if result and "files" in result:
            for f in result["files"]:
                if f.get("path") == file_path:
                    f["content"] = content
                    break
            await self.save_build_result(project_id, result)

    async def delete_project(self, id: str):
        projects = await self.get_all_projects()
        projects = [p for p in projects if p.id != id]
        await self._save_projects(projects)
        
        project_dir = ARTIFACTS_DIR / id
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)

    async def _save_projects(self, projects: List[Project]):
        with open(PROJECTS_FILE, 'w') as f:
            json.dump([p.dict() for p in projects], f, default=self._serialize_datetime, indent=2)
