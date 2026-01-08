import logging
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env at the absolute beginning
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Project, ProjectStatus, GeneratedDoc
from engine.project_manager import ProjectManager, ARTIFACTS_DIR, PROJECTS_FILE
from engine.ai_analyst import AIAnalyst
from engine.ai_designer import AIDesigner
from engine.ai_builder import AIBuilder
from engine.ai_coder import AICoder

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Idea-to-Deploy API (Python/FastAPI)")

@app.get("/")
async def root():
    return {
        "message": "Idea-to-Deploy API is running",
        "status": "online",
        "frontend_url": "http://localhost:3000",
        "documentation": "/docs"
    }

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/debug")
async def debug_info():
    import os
    return {
        "cwd": os.getcwd(),
        "ARTIFACTS_DIR": str(ARTIFACTS_DIR.absolute()),
        "OPENAI_API_KEY_PRESENT": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_API_KEY_START": os.getenv("OPENAI_API_KEY", "")[:7],
        "DATA_DIR": str(DATA_DIR.absolute()),
        "PROJECTS_FILE_EXISTS": PROJECTS_FILE.exists()
    }

# Engine Instances
project_manager = ProjectManager()
ai_analyst = AIAnalyst()
ai_designer = AIDesigner()
ai_builder = AIBuilder()
from engine.project_runner import ProjectRunner

ai_coder = AICoder()
project_runner = ProjectRunner(ARTIFACTS_DIR)

print(f"API: ARTIFACTS_DIR is {ARTIFACTS_DIR.absolute()}")
print(f"API: PROJECTS_FILE is {PROJECTS_FILE.absolute()}")



@app.post("/api/projects/{id}/preview/start")
async def start_preview(id: str, component: str = "backend"):
    """Start the preview server for backend or frontend"""
    # 1. Install Dependencies first
    success, msg = await project_runner.install_dependencies(id, component)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    
    # 2. Assign Port (Simple logic: Backend 8000+ID_HASH, Frontend 3000+ID_HASH)
    # For now, let's use fixed ports for single user mode, or random
    import random
    port = 8000 if component == "backend" else 3000
    # Add offset to avoid conflict with main app
    port += random.randint(1, 100)
    
    # 3. Start Server
    success, msg = await project_runner.start_server(id, component, port)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
        
    return {"status": "running", "port": port, "message": msg}

@app.post("/api/projects/{id}/preview/stop")
async def stop_preview(id: str, component: str):
    await project_runner.stop_server(id, component)
    return {"status": "stopped"}

@app.get("/api/projects/{id}/preview/logs")
async def get_preview_logs(id: str, component: str):
    logs = await project_runner.get_logs(id, component)
    status = await project_runner.check_health(id, component)
    return {"status": status, "logs": logs}

@app.post("/api/projects/{id}/preview/fix")
async def fix_preview_error(id: str, error_log: str, file_path: str):
    """Auto-fix code based on error log"""
    # Fix: Strip ANSI escape codes that might be present in the path if captured from terminal output
    import re
    file_path = re.sub(r'\x1b\[[0-9;]*[mK]', '', file_path).strip()
    
    # Read file content
    project = await project_manager.get_project(id)
    code_dir = ARTIFACTS_DIR / id / "code"
    full_path = code_dir / file_path
    
    if not full_path.exists():
        logger.error(f"Fix Error: File not found at {full_path}")
        raise HTTPException(status_code=404, detail=f"File not found at: {full_path}")
        
    with open(full_path, "r", encoding="utf-8") as f:
        current_code = f.read()
        
    # Generate fix using LLM
    prompt = f"""
    The following code has an error when running.
    
    FILE: {file_path}
    CODE:
    {current_code}
    
    ERROR LOG:
    {error_log}
    
    TASK: Fix the code to resolve the error. Return ONLY the fixed code.
    IMPORTANT: Do NOT output any conversational text, headers, or markdown formatting. Output pure code only. Do not start with # FIX_ERROR.
    """
    
    fixed_code = await ai_coder.llm.generate_content("FIX_ERROR", {}, prompt)
    fixed_code = ai_coder._clean_code(fixed_code)
    
    if not fixed_code or len(fixed_code.strip()) < 10:
        logger.error("Fix Error: Generated code is empty")
        raise HTTPException(status_code=500, detail="Failed to generate a valid fix (returned empty).")
    
    # Save fix
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)
        
    # Attempt to restart the server if it was running
    component = "backend" if "backend" in file_path else "frontend"
    server_key = f"{id}_{component}"
    existing_port = project_runner.ports.get(server_key)
    
    restart_status = "saved"
    if existing_port:
        await project_runner.start_server(id, component, existing_port)
        restart_status = "restarted"
        
    return {"status": "fixed", "file": file_path, "action": restart_status}


class IdeaRequest(BaseModel):
    idea: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/projects", response_model=Project)
async def create_project(request: IdeaRequest):
    if not request.idea:
        raise HTTPException(status_code=400, detail="Idea is required")
    
    name = request.idea[:50] + ("..." if len(request.idea) > 50 else "")
    project = await project_manager.create_project(name, request.idea)
    
    return project

@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    return await project_manager.get_all_projects()

@app.get("/api/projects/{id}", response_model=Project)
async def get_project(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return project

@app.delete("/api/projects/{id}")
async def delete_project(id: str):
    await project_manager.delete_project(id)
    return {"success": True}

@app.get("/api/projects/{id}/docs")
async def get_project_docs(id: str):
     
    docs = await project_manager.get_docs(id)
    return docs

@app.post("/api/projects/{id}/analyze")
async def analyze_project(id: str):
    project = await project_manager.get_project(id)
    print(f"API: --- STARTING ANALYSIS FOR {id} ---")
    print(f"API: Project Name: {project.name if project else 'NOT FOUND'}")
    
    if not project:
        print(f"API: ERROR - Project {id} not found in {PROJECTS_FILE}")
        raise HTTPException(status_code=404, detail=f"Project {id} not found in database. Please refresh.")
    
    await project_manager.update_project_status(id, "ANALYSIS")
    
    logger.info(f"Starting analysis with AIAnalyst Version: {ai_analyst.VERSION}")
    
    category_titles = {
        'REQUIREMENTS': 'Requirement Document',
        'PLANNING': 'Project Planning Document',
        'ARCHITECTURE': 'Technical Architecture & Delivery Plan',
        'IPMP': 'Integrated Project Management Plan (IPMP)',
        'SCHEDULE_COST': 'Schedule & Cost Plan',
        'QUALITY_RISK': 'Quality, Risk & Procurement Plan',
        'TESTING_RELEASE': 'Testing & Release Plan'
    }
    
    saved_docs = []
    
    async def on_doc_generated(category: str, content: str):
        if category in category_titles:
            title = category_titles[category]
            print(f"API: GENERATED {category} (length: {len(content)})")
            saved = await project_manager.save_doc(id, category, title, content)
            saved_docs.append(saved)
            logger.info(f"Incremental Save: {title} for project {id}")
        else:
            print(f"API: WARNING - Category {category} not in category_titles. Skipping save to UI.")

    try:
        # Pass project_id and callback to enable design artifact generation and incremental UI updates
        docs = await ai_analyst.analyze_idea(project.description, project_id=id, on_doc_generated=on_doc_generated)
            
        if not saved_docs:
            logger.error(f"Analysis failed for project {id}: No documents were saved. Check API keys and logs.")
            await project_manager.update_project_status(id, "NEW")
            raise HTTPException(status_code=500, detail="AI failed to generate any documents. Please check your API key and try again.")

        await project_manager.update_project_status(id, "PLANNING")
        return {"success": True, "docs": saved_docs}
    except Exception as e:
        logger.error(f"Analysis Error for project {id}: {str(e)}")
        await project_manager.update_project_status(id, "NEW")
        raise HTTPException(status_code=500, detail=f"Generation Failed: {str(e)}")

@app.post("/api/projects/{id}/design")
async def design_project(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "DESIGN")
    
    # AIDesigner now returns a list of visuals (currently empty in our simplified version)
    # but more importantly, it saves the page_list_wireframe.txt file.
    # We will also save it as a document in docs.json for the UI to display in the Docs tab.
    
    try:
        visuals = await ai_designer.generate_visuals(id, project.description)
        
        # Read the text file we just saved to store it as a doc
        screen_list_path = ARTIFACTS_DIR / id / "docs" / "screen_list.txt"
        if screen_list_path.exists():
            with open(screen_list_path, 'r', encoding='utf-8') as f:
                screen_content = f.read()
                await project_manager.save_doc(id, "SCREEN_LIST", "Screen Inventory", screen_content)
        
        await project_manager.save_visuals(id, visuals)
        await project_manager.update_project_status(id, "DESIGNED")
        
        return {"success": True, "visuals": visuals}
    except Exception as e:
        logger.error(f"Design Error for project {id}: {str(e)}")
        await project_manager.update_project_status(id, "PLANNING")
        raise HTTPException(status_code=500, detail=f"Design Failed: {str(e)}")

@app.get("/api/projects/{id}/wireframes/{filename:path}")
async def serve_wireframe(id: str, filename: str):
    # Support new structure: designs/wireframes/images or html
    # Check images first if extension is png
    possible_paths = [
        ARTIFACTS_DIR / id / "designs" / "wireframes" / "images" / filename,
        ARTIFACTS_DIR / id / "designs" / "wireframes" / "html" / filename,
        ARTIFACTS_DIR / id / "wireframes" / filename,
    ]
    
    file_path = None
    for p in possible_paths:
        if p.exists():
            file_path = p
            break
            
    if not file_path:
        # Fallback for index
        index_path = ARTIFACTS_DIR / id / "designs" / "wireframes" / "html" / "index.html"
        if index_path.exists():
             file_path = index_path
        else:
             raise HTTPException(status_code=404, detail=f"Wireframe '{filename}' not found.")
             
    return FileResponse(file_path)

@app.get("/api/projects/{id}/ui/{filename:path}")
async def serve_ui(id: str, filename: str):
    # High-Fi UI stored in ARTIFACTS_DIR/:id/ui
    file_path = ARTIFACTS_DIR / id / "ui" / filename
    if not file_path.exists():
        if (file_path.with_suffix(".html")).exists():
            file_path = file_path.with_suffix(".html")
        elif (ARTIFACTS_DIR / id / "ui" / "index.html").exists():
            file_path = ARTIFACTS_DIR / id / "ui" / "index.html"
        else:
            raise HTTPException(status_code=404, detail=f"UI Prototype '{filename}' not found.")
    return FileResponse(file_path)

@app.get("/api/projects/{id}/visuals/{filename:path}")
async def serve_visual_file(id: str, filename: str):
    file_path = ARTIFACTS_DIR / id / "visuals" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Visual '{filename}' not found.")
    return FileResponse(file_path)

@app.get("/api/projects/{id}/visuals")
async def get_project_visuals(id: str):
    return await project_manager.get_visuals(id)

@app.post("/api/projects/{id}/build")
async def build_project(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "CODING")
    
    try:
        build_result = await ai_builder.build_project(id, project.description)
        await project_manager.save_build_result(id, build_result)
        
        await project_manager.update_project_status(id, "COMPLETED")
        
        return build_result
    except Exception as e:
        logger.error(f"Build Error for project {id}: {str(e)}")
        await project_manager.update_project_status(id, "DESIGNED")
        raise HTTPException(status_code=500, detail=f"Build Failed: {str(e)}")

@app.get("/api/projects/{id}/build")
async def get_project_build(id: str):
    # Try to read generated code from disk first (AICoder output)
    build_result = await project_manager.read_generated_code(id)
    
    if build_result:
        return build_result

    # Fallback to stored build.json (Old AIBuilder output)
    build_result = await project_manager.get_build_result(id)
    
    return build_result

class UpdateFileRequest(BaseModel):
    path: str
    content: str

@app.put("/api/projects/{id}/build/file")
async def update_project_file(id: str, request: UpdateFileRequest):
    await project_manager.update_file_content(id, request.path, request.content)
    return {"success": True}

# Code Generation Endpoints


@app.get("/api/projects/{id}/code/download")
async def download_code(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project_name = project.name
    zip_filename = f"{project_name.lower().replace(' ', '-')}-generated.zip"
    zip_path = ARTIFACTS_DIR / id / zip_filename
    
    if not zip_path.exists():
         raise HTTPException(status_code=404, detail="Code package not found. Please generate code first.")
         
    return FileResponse(zip_path, media_type='application/zip', filename=zip_filename)

@app.post("/api/admin/backfill-wireframes")
async def backfill_wireframes(limit: int = 1000):
    import logging
    logger.info(f"Starting wireframe backfill with limit={limit}")
    projects = await project_manager.get_all_projects()
    results = []
    
    import re
    import uuid
    import aiohttp

    async with aiohttp.ClientSession() as session:
        for project in projects:
            try:
                # Check for existing visuals but respect force/limit if needed
                # For now, let's just append if missing
                existing_visuals = await project_manager.get_visuals(project.id)
                
                # Get/Parse Docs (Same logic)
                docs = await project_manager.get_docs(project.id)
                screen_doc = next((d for d in docs if "screen" in d.title.lower() or "page list" in d.title.lower()), None)
                
                if not screen_doc:
                     results.append(f"Project {project.name}: No screen doc")
                     continue
                
                # Parse Logic
                content = screen_doc.content
                screens = []
                current_screen = None
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
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
                
                # Filter missing
                existing_titles = {v['title'].lower() for v in existing_visuals}
                missing_screens = [s for s in screens if s['title'].lower() not in existing_titles]
                
                # Apply LIMIT here
                to_generate = missing_screens[:limit]
                
                if not to_generate:
                     results.append(f"Project {project.name}: Up to date (Checked {len(missing_screens)} missing against limit {limit})")
                     continue

                generated_count = 0
                for screen in to_generate:
                    image_prompt = (
                        f"Create a LOW-FIDELITY UX WIREFRAME ONLY for a screen named '{screen['title']}'. "
                        f"Context: {screen['desc']}. "
                        f"STRICT RULES: Black and white only, NO colors, NO gradients, NO shadows, NO illustrations, NO photos, NO realistic UI, NO styling. "
                        f"DESIGN STYLE: Rough product wireframe, Figma / Balsamiq style. Simple rectangles, lines, and placeholder text only. "
                        f"Use boxes labeled like: Header, Sidebar, Button, Image, Text, Input. Flat 2D layout. "
                        f"Looks hand-sketched or system-designed, NOT AI-art. "
                        f"PURPOSE: Functional screen structure, Layout planning only. "
                    )
                    
                    image_url = await ai_designer.llm.generate_image(image_prompt)
                    if image_url:
                        filename = f"{uuid.uuid4()}.png"
                        file_save_path = ARTIFACTS_DIR / project.id / "visuals" / filename
                        file_save_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        async with session.get(image_url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                with open(file_save_path, "wb") as f:
                                    f.write(data)
                                
                                existing_visuals.append({
                                    "id": str(uuid.uuid4()),
                                    "title": screen['title'],
                                    "screenName": screen['title'],
                                    "description": screen['desc'][:100] + "...",
                                    "imageUrl": f"/api/projects/{project.id}/visuals/{filename}",
                                    "localPath": str(file_save_path),
                                })
                                generated_count += 1
                
                if generated_count > 0:
                    await project_manager.save_visuals(project.id, existing_visuals)
                    results.append(f"Project {project.name}: Generated {generated_count} new wireframes")
                else:
                    results.append(f"Project {project.name}: No new wireframes needed")
                    
            except Exception as e:
                results.append(f"Project {project.name}: Error - {str(e)}")
                
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
