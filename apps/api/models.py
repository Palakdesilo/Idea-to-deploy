from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid

ProjectStatus = Literal['NEW', 'ANALYSIS', 'PLANNING', 'DESIGN', 'DESIGNED', 'CODING', 'COMPLETED', 'FAILED']
DocCategory = Literal['REQUIREMENTS', 'PLANNING', 'ARCHITECTURE', 'IPMP', 'SCHEDULE_COST', 'QUALITY_RISK', 'TESTING_RELEASE', 'UI_UX']

class ProjectMetrics(BaseModel):
    progress: int = 0
    currentPhase: str = "Initialization"
    lastUpdated: datetime = Field(default_factory=datetime.now)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    createdAt: datetime = Field(default_factory=datetime.now)
    status: ProjectStatus = "NEW"
    metrics: ProjectMetrics = Field(default_factory=ProjectMetrics)

class GeneratedDoc(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str
    category: DocCategory
    title: str
    content: str
    isFinal: bool = True

class UIAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str
    screenName: str
    description: str
    imageUrl: Optional[str] = None
    promptUsed: str
    purpose: Optional[str] = None
    roles: Optional[List[str]] = None
    components: Optional[List[str]] = None
    interactions: Optional[List[str]] = None
    states: Optional[List[str]] = None

class BuildResult(BaseModel):
    projectId: str
    files: List[Dict[str, Any]]
    stats: Optional[Dict[str, Any]] = None
