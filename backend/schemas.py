"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    description: str
    appType: str = "web-app"
    useDb: bool = False
    useApis: bool = False
    userAuth: bool = False
    intensiveTesting: bool = False
    workerCount: int = 3

class ChatMessage(BaseModel):
    """Schema for chat messages."""
    sender: str
    text: str

class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: str
    description: str
    appType: str
    useDb: bool
    useApis: bool
    userAuth: bool
    intensiveTesting: bool
    workerCount: int
    isComplete: bool
    currentStage: str
    taskPlan: List[Dict[str, Any]]
    chatHistory: List[Dict[str, str]]
    uploadedFiles: List[str]
    
    class Config:
        orm_mode = True

class PreviewResponse(BaseModel):
    """Schema for preview response."""
    appType: str
    description: str
    status: str
    isComplete: bool
