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
    # Primary data folder at project root
    data_path = Path(r"D:\Palak\Idea-to-deploy\data")
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
    return data_path

DATA_DIR = find_data_dir()
PROJECTS_FILE = DATA_DIR / "projects.json"
ARTIFACTS_DIR = DATA_DIR / "artifacts"

import asyncio

class ProjectManager:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        self.lock = asyncio.Lock()
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
        
        try:
            with open(PROJECTS_FILE, 'r') as f:
                data = json.load(f)
            
            # 1. Sync JSON -> Disk (Remove entries from JSON if folder missing)
            valid_projects = []
            projects_to_keep = []
            existing_ids = set()
            
            dirty = False
            for p_data in data:
                p_id = p_data.get('id')
                if p_id and (ARTIFACTS_DIR / p_id).exists():
                    valid_projects.append(Project(**p_data))
                    projects_to_keep.append(p_data)
                    existing_ids.add(p_id)
                else:
                    # Project folder is missing, mark as dirty to clean up projects.json later
                    dirty = True
            
            # 2. Sync Disk -> JSON (Add entries to JSON if folder exists but missing in JSON)
            # This handles the case where a user sees folders that are not in the UI
            if ARTIFACTS_DIR.exists():
                for item in os.listdir(ARTIFACTS_DIR):
                    item_path = ARTIFACTS_DIR / item
                    if item_path.is_dir():
                        if item not in existing_ids:
                            # It's an orphan! Recover it.
                            print(f"ProjectManager: Found orphaned project folder {item}, recovering...")
                            
                            recovered_project = Project(
                                id=item,
                                name=f"Recovered Project ({item[:8]})",
                                description="Recovered from disk artifacts.",
                                createdAt=datetime.now(),
                                status="COMPLETED",
                                metrics={
                                    "progress": 100,
                                    "currentPhase": "Recovered",
                                    "lastUpdated": datetime.now()
                                }
                            )
                            valid_projects.append(recovered_project)
                            projects_to_keep.append(recovered_project.dict())
                            dirty = True

            if dirty:
                print("ProjectManager: Synchronizing projects.json with filesystem...")
                with open(PROJECTS_FILE, 'w') as f:
                    json.dump(projects_to_keep, f, default=self._serialize_datetime, indent=2)
            
            return valid_projects
        except Exception as e:
            print(f"ProjectManager: Error loading projects: {e}")
            return []

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
        print(f"ProjectManager: FETCHING docs from {docs_file.absolute()}")
        if not docs_file.exists():
            print(f"ProjectManager: Docs file NOT FOUND at {docs_file.absolute()}")
            return []
        with open(docs_file, 'r') as f:
            try:
                data = json.load(f)
                return [GeneratedDoc(**d) for d in data]
            except Exception as e:
                print(f"ProjectManager: ERROR loading docs.json: {e}")
                return []

    async def save_doc(self, project_id: str, category: str, title: str, content: str) -> GeneratedDoc:
        doc = GeneratedDoc(
            projectId=project_id,
            category=category,
            title=title,
            content=content
        )
        
        project_dir = ARTIFACTS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        docs_file = project_dir / "docs.json"
        print(f"ProjectManager: SAVING doc {title} to {docs_file.absolute()}")
        docs = []
        async with self.lock:
            if docs_file.exists():
                with open(docs_file, 'r') as f:
                    try:
                        docs_data = json.load(f)
                        docs = [GeneratedDoc(**d) for d in docs_data]
                    except Exception as e:
                        print(f"ProjectManager: Error reading docs.json: {e}")
                    
            # Remove old doc of same category
            docs = [d for d in docs if d.category != category]
            docs.append(doc)
            
            with open(docs_file, 'w') as f:
                print(f"ProjectManager: Saving doc {title} to {docs_file}")
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
        project_dir = ARTIFACTS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Save build.json (Metadata and full list)
        build_file = project_dir / "build.json"
        with open(build_file, 'w') as f:
            json.dump(build_result, f, default=self._serialize_datetime, indent=2)
            
        # 2. Persist files to 'code' directory for exploration and download
        if isinstance(build_result, dict) and "files" in build_result:
            code_dir = project_dir / "code"
            # Optional: Clean code dir if it exists to avoid stale files?
            # For now, just write/overwrite
            for file_info in build_result["files"]:
                path = file_info.get("path")
                content = file_info.get("content", "")
                if path:
                    # Security: Ensure path is relative and doesn't escape code_dir
                    # We convert to string, remove leading / or \, and then resolve
                    clean_path = str(path).lstrip('/').lstrip('\\')
                    # If it's something like C:\... we remove the drive
                    if ':' in clean_path:
                        clean_path = clean_path.split(':')[-1].lstrip('/').lstrip('\\')
                    
                    full_path = (code_dir / clean_path).resolve()
                    if not str(full_path).startswith(str(code_dir.resolve())):
                         print(f"SECURITY WARNING: Attempted path escape blocked: {path}")
                         continue

                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)

            # 3. Create ZIP package for download
            import zipfile
            # Use project name if possible, else use ID
            zip_filename = f"{project_id}-generated.zip"
            # Try to get project name for a nicer filename if possible (main.py does this too)
            zip_path = project_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in code_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(code_dir)
                        zipf.write(file_path, arcname)

    async def update_file_content(self, project_id: str, file_path: str, content: str):
        result = await self.get_build_result(project_id)
        if result and "files" in result:
            for f in result["files"]:
                if f.get("path") == file_path:
                    f["content"] = content
                    break
            await self.save_build_result(project_id, result)

    async def delete_project(self, id: str):
        # 1. Update JSON first (optimistic delete)
        projects = await self.get_all_projects()
        projects = [p for p in projects if p.id != id]
        await self._save_projects(projects)
        
        # 2. Delete Folder with Robust Error Handling
        project_dir = ARTIFACTS_DIR / id
        if project_dir.exists():
            import shutil
            import stat
            import time

            def on_rm_error(func, path, exc_info):
                # path contains the path of the file that couldn't be removed
                # let's just assume that it's read-only and unlink it.
                os.chmod(path, stat.S_IWRITE)
                try:
                    os.unlink(path)
                except Exception as e:
                    print(f"ProjectManager: Failed to force delete {path}: {e}")

            try:
                shutil.rmtree(project_dir, onerror=on_rm_error)
            except Exception as e:
                print(f"ProjectManager: Standard rmtree failed for {project_dir}: {e}")
                # Retry once after a small delay
                time.sleep(0.5)
                try:
                    shutil.rmtree(project_dir, onerror=on_rm_error)
                except Exception as e2:
                    print(f"ProjectManager: Retry rmtree failed for {project_dir}: {e2}")

    async def read_generated_code(self, project_id: str) -> Optional[Any]:
        code_dir = ARTIFACTS_DIR / project_id / "code"
        if not code_dir.exists():
            return None
            
        files = []
        # Define ignored directories and files
        ignored_dirs = {
            'node_modules', '.next', '__pycache__', '.git', 
            '.pytest_cache', 'dist', 'build', 'coverage', 
            'venv', 'env', '.idea', '.vscode'
        }
        ignored_files = {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 
            '.DS_Store', 'Thumbs.db'
        }

        for file_path in code_dir.rglob('*'):
            if file_path.is_file():
                # Check if file is in an ignored directory
                parts = file_path.relative_to(code_dir).parts
                if any(part in ignored_dirs for part in parts):
                    continue
                    
                if file_path.name in ignored_files:
                    continue

                try:
                     # Attempt to read as text, skip binary
                     # Limit file size to avoid loading huge files (e.g. 1MB limit)
                     if file_path.stat().st_size > 1_000_000:
                         continue

                     with open(file_path, 'r', encoding='utf-8') as f:
                         content = f.read()
                         rel_path = file_path.relative_to(code_dir).as_posix()
                         files.append({
                             "path": rel_path,
                             "content": content
                         })
                except UnicodeDecodeError:
                    pass # Skip binary files
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    
        return {"files": files}

    async def _save_projects(self, projects: List[Project]):
        with open(PROJECTS_FILE, 'w') as f:
            json.dump([p.dict() for p in projects], f, default=self._serialize_datetime, indent=2)
