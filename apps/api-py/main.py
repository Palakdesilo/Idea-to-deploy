import logging
import sys
import os
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

# Add current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Project, ProjectStatus, GeneratedDoc
from engine.project_manager import ProjectManager
from engine.ai_analyst import AIAnalyst
from engine.ai_designer import AIDesigner
from engine.ai_builder import AIBuilder

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Idea-to-Deploy API (Python/FastAPI)")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to the Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine Instances
project_manager = ProjectManager()
ai_analyst = AIAnalyst()
ai_designer = AIDesigner()
ai_builder = AIBuilder()

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
    
    docs = await ai_analyst.analyze_idea(project.description)
    
    category_titles = {
        'REQUIREMENTS': 'Requirement Document',
        'PLANNING': 'Project Planning Document',
        'ARCHITECTURE': 'Technical Architecture & Delivery Plan',
        'IPMP': 'Integrated Project Management Plan (IPMP)',
        'SCHEDULE_COST': 'Schedule & Cost Plan',
        'QUALITY_RISK': 'Quality, Risk & Procurement Plan',
        'TESTING_RELEASE': 'Testing & Release Plan',
        'UI_UX': 'UI/UX Design Specification'
    }
    
    saved_docs = []
    for category, content in docs.items():
        title = category_titles.get(category, f"{category} Document")
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
    build_result = await project_manager.get_build_result(id)
    
    if not build_result:
        project = await project_manager.get_project(id)
        if project and project.status == "COMPLETED":
            build_result = await ai_builder.build_project(id, project.description)
            await project_manager.save_build_result(id, build_result)
            
    return build_result

class UpdateFileRequest(BaseModel):
    path: str
    content: str

@app.put("/api/projects/{id}/build/file")
async def update_project_file(id: str, request: UpdateFileRequest):
    await project_manager.update_file_content(id, request.path, request.content)
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
