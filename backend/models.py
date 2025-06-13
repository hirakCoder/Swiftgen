from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class GenerateRequest(BaseModel):
    description: str
    app_name: Optional[str] = None
    project_id: Optional[str] = None
    ios_version: Optional[str] = "17.0"  # Default to iOS 17.0

class BuildStatus(BaseModel):
    status: str  # 'pending', 'building', 'success', 'failed'
    message: str
    timestamp: datetime = datetime.now()

class BuildResult(BaseModel):
    success: bool
    errors: List[str] = []
    warnings: List[str] = []
    build_time: float
    log_path: str
    app_path: Optional[str] = None
    simulator_launched: bool = False
    simulator_message: Optional[str] = None
    runtime_crash: bool = False  # Add this field

class ProjectStatus(BaseModel):
    project_id: str
    app_name: str
    created_at: str
    bundle_id: str
    files: List[str]
    app_built: bool
    project_path: str