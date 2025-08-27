"""Workflow simulation for AI agents."""
import asyncio
from sqlalchemy.orm import Session
from .models import Project

# Mock workflow definitions
MOCK_TASKS = [
    {"name": "Define Database Schema", "agent": "Worker"},
    {"name": "Set up FastAPI server", "agent": "Worker"},
    {"name": "Create API endpoint for user registration", "agent": "Worker"},
    {"name": "Build frontend login form", "agent": "Worker"},
    {"name": "Write unit tests for API", "agent": "Tester"}
]

STAGES = [
    {"name": "manager", "duration": 1.0, "text": "Manager: Analyzing request..."},
    {"name": "retriever", "duration": 1.0, "text": "Retriever: Searching knowledge base..."},
    {"name": "worker", "duration": 3.0, "text": "Worker: Executing tasks..."},
    {"name": "tester", "duration": 1.5, "text": "Tester: Validating final output..."},
]

async def simulate_workflow(project_id: str, db: Session):
    """Simulate the AI agent workflow."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return

    # Reset state
    project.is_complete = False
    project.current_stage = 'Starting...'
    project.task_plan = [dict(t, status='pending') for t in MOCK_TASKS]
    db.commit()

    # Manager stage
    project.current_stage = STAGES[0]['text']
    db.commit()
    await asyncio.sleep(STAGES[0]['duration'])

    # Retriever stage
    project.current_stage = STAGES[1]['text']
    db.commit()
    await asyncio.sleep(STAGES[1]['duration'])

    # Worker stage
    project.current_stage = STAGES[2]['text']
    db.commit()
    worker_tasks = [i for i, t in enumerate(MOCK_TASKS) if t['agent'] == 'Worker']
    if worker_tasks:
        per_task = STAGES[2]['duration'] / max(1, len(worker_tasks))
        for idx in worker_tasks:
            project.task_plan[idx]['status'] = 'running'
            db.commit()
            await asyncio.sleep(per_task)
            project.task_plan[idx]['status'] = 'completed'
            db.commit()

    # Tester stage
    project.current_stage = STAGES[3]['text']
    db.commit()
    tester_tasks = [i for i, t in enumerate(MOCK_TASKS) if t['agent'] == 'Tester']
    if tester_tasks:
        per_task = STAGES[3]['duration'] / max(1, len(tester_tasks))
        for idx in tester_tasks:
            project.task_plan[idx]['status'] = 'running'
            db.commit()
            await asyncio.sleep(per_task)
            project.task_plan[idx]['status'] = 'completed'
            db.commit()

    # Complete
    project.current_stage = 'Build Complete! Ready to Deploy.'
    project.is_complete = True
    project.chat_history.append({
        'sender': 'system',
        'text': 'Build completed. Preview available.'
    })
    db.commit()
