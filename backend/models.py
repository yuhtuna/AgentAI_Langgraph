"""Database models for AgentAI backend."""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    app_type = Column(String, default="web-app")
    use_db = Column(Boolean, default=False)
    use_apis = Column(Boolean, default=False)
    user_auth = Column(Boolean, default=False)
    intensive_testing = Column(Boolean, default=False)
    worker_count = Column(Integer, default=3)
    
    # Workflow state
    is_complete = Column(Boolean, default=False)
    current_stage = Column(String, default="Queued")
    task_plan = Column(JSON, default=list)
    chat_history = Column(JSON, default=list)
    
    # File uploads
    uploaded_files = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'id': self.id,
            'description': self.description,
            'appType': self.app_type,
            'useDb': self.use_db,
            'useApis': self.use_apis,
            'userAuth': self.user_auth,
            'intensiveTesting': self.intensive_testing,
            'workerCount': self.worker_count,
            'isComplete': self.is_complete,
            'currentStage': self.current_stage,
            'taskPlan': self.task_plan,
            'chatHistory': self.chat_history,
            'uploadedFiles': self.uploaded_files,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
