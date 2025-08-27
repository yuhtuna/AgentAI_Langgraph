"""FastAPI server for AgentAI backend."""
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
import aiofiles

from .database import get_db, create_tables
from .models import Project
from .schemas import ProjectCreate, ChatMessage, ProjectResponse, PreviewResponse
from .workflow import simulate_workflow

# Constants
PROJECT_NOT_FOUND = "Project not found"

# Create database tables
create_tables()

# File upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="AgentAI Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "AgentAI Backend is running"}

@app.post("/projects", response_model=dict)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new project."""
    project_id = uuid.uuid4().hex
    
    project = Project(
        id=project_id,
        description=project_data.description,
        app_type=project_data.appType,
        use_db=project_data.useDb,
        use_apis=project_data.useApis,
        user_auth=project_data.userAuth,
        intensive_testing=project_data.intensiveTesting,
        worker_count=project_data.workerCount,
        chat_history=[{
            'sender': 'system',
            'text': f'Starting project: "{project_data.description}" (Type: {project_data.appType}, Workers: {project_data.workerCount})'
        }]
    )
    
    db.add(project)
    db.commit()
    
    # Start workflow simulation in background
    background_tasks.add_task(simulate_workflow, project_id, db)
    
    return {"project_id": project_id}

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get project details."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=PROJECT_NOT_FOUND)
    return project

@app.post("/projects/{project_id}/chat")
async def add_chat_message(
    project_id: str,
    message: ChatMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Add a chat message to the project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=PROJECT_NOT_FOUND)
    
    project.chat_history.append({
        'sender': message.sender,
        'text': message.text
    })
    
    # If project is complete, restart workflow
    if project.is_complete:
        background_tasks.add_task(simulate_workflow, project_id, db)
        project.chat_history.append({
            'sender': 'system',
            'text': 'Rebuilding project based on your message...'
        })
    
    db.commit()
    return {"status": "success"}

@app.post("/projects/{project_id}/upload")
async def upload_files(
    project_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload files for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=PROJECT_NOT_FOUND)
    
    saved_files = []
    upload_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        project.uploaded_files.append(file.filename)
        saved_files.append(file.filename)
    
    db.commit()
    return {"saved_files": saved_files}

@app.get("/projects/{project_id}/preview", response_model=PreviewResponse)
async def get_preview(project_id: str, db: Session = Depends(get_db)):
    """Get project preview data."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=PROJECT_NOT_FOUND)
    
    return PreviewResponse(
        appType=project.app_type,
        description=project.description,
        status=project.current_stage,
        isComplete=project.is_complete
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
