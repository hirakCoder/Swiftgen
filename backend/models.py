from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime

class GenerateRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=5000)
    app_name: Optional[str] = Field(None, min_length=1, max_length=50)
    project_id: Optional[str] = Field(None, min_length=1, max_length=100)
    ios_version: Optional[str] = Field("17.0", pattern=r"^\d{2}\.\d$")
    
    @validator('app_name')
    def validate_app_name(cls, v):
        if v:
            # Remove spaces and special characters
            clean_name = ''.join(c for c in v if c.isalnum() or c in '-_')
            if not clean_name:
                raise ValueError("App name must contain at least one alphanumeric character")
            return clean_name
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v.strip()

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

class ModifyRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=100)
    modification: str = Field(..., min_length=5, max_length=5000)
    
    @validator('modification')
    def validate_modification(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError("Modification description must be at least 5 characters long")
        return v.strip()