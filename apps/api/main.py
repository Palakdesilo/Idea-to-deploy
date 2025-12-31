import logging
import sys
import os
from fastapi import FastAPI, HTTPException, Request, Response, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Project, ProjectStatus, GeneratedDoc
from engine.project_manager import ProjectManager, ARTIFACTS_DIR
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

# Engine Instances
project_manager = ProjectManager()
ai_analyst = AIAnalyst()
ai_designer = AIDesigner()
ai_builder = AIBuilder()
from engine.project_runner import ProjectRunner

ai_coder = AICoder()
project_runner = ProjectRunner(ARTIFACTS_DIR)

# ... (keep existing endpoints) ...

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
    
    # Save fix
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
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "ANALYSIS")
    
    logger.info(f"Starting analysis with AIAnalyst Version: {ai_analyst.VERSION}")
    
    # Pass project_id to enable design artifact generation
    docs = await ai_analyst.analyze_idea(project.description, project_id=id)
    
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
    for category, content in docs.items():
        if category in category_titles:
            title = category_titles[category]
            saved = await project_manager.save_doc(id, category, title, content)
            saved_docs.append(saved)
        
    await project_manager.update_project_status(id, "PLANNING")
    
    return {"success": True, "docs": saved_docs}

@app.post("/api/projects/{id}/design")
async def design_project(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "DESIGN")
    
    visuals = await ai_designer.generate_visuals(id, project.description)
    await project_manager.save_visuals(id, visuals)
    
    await project_manager.update_project_status(id, "DESIGNED")
    
    return {"success": True, "visuals": visuals}

@app.get("/api/projects/{id}/wireframes/{filename:path}")
async def serve_wireframe(id: str, filename: str):
    # We assume wireframes are stored in ARTIFACTS_DIR/:id/wireframes
    file_path = ARTIFACTS_DIR / id / "wireframes" / filename
    if not file_path.exists():
        if (file_path.with_suffix(".html")).exists():
            file_path = file_path.with_suffix(".html")
        elif (ARTIFACTS_DIR / id / "wireframes" / "index.html").exists():
            file_path = ARTIFACTS_DIR / id / "wireframes" / "index.html"
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

@app.get("/api/projects/{id}/visuals")
async def get_project_visuals(id: str):
    return await project_manager.get_visuals(id)

@app.post("/api/projects/{id}/build")
async def build_project(id: str):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "CODING")
    
    build_result = await ai_builder.build_project(id, project.description)
    await project_manager.save_build_result(id, build_result)
    
    await project_manager.update_project_status(id, "COMPLETED")
    
    return build_result

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

@app.post("/api/projects/{id}/generate-code")
async def generate_code(id: str, background_tasks: BackgroundTasks):
    project = await project_manager.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await project_manager.update_project_status(id, "CODING")
    
    async def generate_task(project_id, project_name, description):
        try:
            logger.info(f"Starting code generation for {project_id}")
            await ai_coder.generate_full_stack_app(project_id, project_name, description)
            await project_manager.update_project_status(project_id, "COMPLETED")
            logger.info(f"Code generation completed for {project_id}")
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            await project_manager.update_project_status(project_id, "FAILED")

    background_tasks.add_task(generate_task, id, project.name, project.description)
    
    return {"message": "Code generation started", "status": "CODING"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
