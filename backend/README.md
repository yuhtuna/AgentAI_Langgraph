Backend FastAPI server for AgentAI

Endpoints:
- GET /health
- POST /projects
- GET /projects/{project_id}
- POST /projects/{project_id}/chat
- POST /projects/{project_id}/upload
- GET /projects/{project_id}/preview

Run locally:
    pip install -r requirements.txt
    uvicorn backend.server:app --reload

Note: This uses an in-memory store for simplicity. For production, connect to a database and persistent storage.
