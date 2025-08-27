"""FastAPI server for AgentAI backend.

Provides endpoints the frontend can use to create projects, upload files, post chat messages,
and fetch project status and preview.

Run with:
    uvicorn backend.server:app --reload
"""
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uuid
import os
import aiofiles

# Simple in-memory store for projects
projects: Dict[str, Dict[str, Any]] = {}
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="AgentAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class StartProjectRequest(BaseModel):
    description: str
    appType: str = "web-app"
    useDb: bool = False
    useApis: bool = False
    userAuth: bool = False
    intensiveTesting: bool = False
    workerCount: int = 3

class ChatMessage(BaseModel):
    sender: str
    text: str

# --- Mock workflow definitions (kept similar to frontend) ---
mock_tasks = [
    {"name": "Define Database Schema", "agent": "Worker"},
    {"name": "Set up FastAPI server", "agent": "Worker"},
    {"name": "Create API endpoint for user registration", "agent": "Worker"},
    {"name": "Build frontend login form", "agent": "Worker"},
    {"name": "Write unit tests for API", "agent": "Tester"}
]

stages = [
    {"name": "manager", "duration": 1.0, "text": "Manager: Analyzing request..."},
    {"name": "retriever", "duration": 1.0, "text": "Retriever: Searching knowledge base..."},
    {"name": "worker", "duration": 3.0, "text": "Worker: Executing tasks..."},
    {"name": "tester", "duration": 1.5, "text": "Tester: Validating final output..."},
]

# --- Helper: simulate workflow in background ---
async def simulate_workflow(project_id: str):
    project = projects.get(project_id)
    if not project:
        return

    # reset state
    project['isComplete'] = False
    project['currentStage'] = 'Starting...'
    project['taskPlan'] = [dict(t, status='pending') for t in mock_tasks]

    # Manager
    project['currentStage'] = stages[0]['text']
    await asyncio.sleep(stages[0]['duration'])

    # Retriever
    project['currentStage'] = stages[1]['text']
    await asyncio.sleep(stages[1]['duration'])

    # Worker: run worker tasks
    project['currentStage'] = stages[2]['text']
    worker_tasks = [i for i, t in enumerate(mock_tasks) if t['agent'] == 'Worker']
    if worker_tasks:
        per_task = stages[2]['duration'] / max(1, len(worker_tasks))
        for idx in worker_tasks:
            project['taskPlan'][idx]['status'] = 'running'
            await asyncio.sleep(per_task)
            project['taskPlan'][idx]['status'] = 'completed'

    # Tester
    project['currentStage'] = stages[3]['text']
    tester_tasks = [i for i, t in enumerate(mock_tasks) if t['agent'] == 'Tester']
    if tester_tasks:
        per_task = stages[3]['duration'] / max(1, len(tester_tasks))
        for idx in tester_tasks:
            project['taskPlan'][idx]['status'] = 'running'
            await asyncio.sleep(per_task)
            project['taskPlan'][idx]['status'] = 'completed'

    project['currentStage'] = 'Build Complete! Ready to Deploy.'
    project['isComplete'] = True
    project['chatHistory'].append({
        'sender': 'system',
        'text': 'Build completed. Preview available.'
    })

# --- Endpoints ---
@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.post('/projects')
async def create_project(payload: StartProjectRequest, background_tasks: BackgroundTasks):
    project_id = uuid.uuid4().hex
    project = {
        'id': project_id,
        'description': payload.description,
        'appType': payload.appType,
        'useDb': payload.useDb,
        'useApis': payload.useApis,
        'userAuth': payload.userAuth,
        'intensiveTesting': payload.intensiveTesting,
        'workerCount': payload.workerCount,
        'isComplete': False,
        'currentStage': 'Queued',
        'taskPlan': [],
        'chatHistory': [
            {'sender': 'system', 'text': f'Starting project: "{payload.description}" (Type: {payload.appType}, Workers: {payload.workerCount})'}
        ],
        'uploadedFiles': []
    }
    projects[project_id] = project
    # start simulation in background
    background_tasks.add_task(asyncio.create_task, simulate_workflow(project_id))
    return {'project_id': project_id}

@app.get('/projects/{project_id}')
async def get_project(project_id: str):
    project = projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    return project

@app.post('/projects/{project_id}/chat')
async def post_chat(project_id: str, message: ChatMessage, background_tasks: BackgroundTasks):
    project = projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    project['chatHistory'].append({'sender': message.sender, 'text': message.text})
    # optional: re-run workflow if user asks for changes
    if project.get('isComplete'):
        # start a short re-run to simulate rework
        background_tasks.add_task(asyncio.create_task, simulate_workflow(project_id))
        project['chatHistory'].append({'sender': 'system', 'text': 'Rebuilding project based on your message...'})
    return {'ok': True}

@app.post('/projects/{project_id}/upload')
async def upload_files(project_id: str, files: List[UploadFile] = File(...)):
    project = projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    saved = []
    dest_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(dest_dir, exist_ok=True)
    for upload in files:
        filename = upload.filename
        dest_path = os.path.join(dest_dir, filename)
        async with aiofiles.open(dest_path, 'wb') as out_file:
            content = await upload.read()
            await out_file.write(content)
        project['uploadedFiles'].append(filename)
        saved.append(filename)
    return {'saved': saved}

@app.get('/projects/{project_id}/preview')
async def preview(project_id: str):
    project = projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    # Minimal preview data
    return {
        'appType': project['appType'],
        'description': project['description'],
        'status': project['currentStage'],
        'isComplete': project['isComplete']
    }

# Allow running directly: python -m backend.server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.server:app', host='127.0.0.1', port=8000, reload=True)
