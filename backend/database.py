"""Database configuration for AgentAI backend."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./backend/projects.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""SQLite database setup for AgentAI backend."""
from sqlalchemy import create_engine, Column, String, Text, Boolean, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import JSON
import datetime

DATABASE_URL = "sqlite:///./backend/projects.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    appType = Column(String, default="web-app")
    useDb = Column(Boolean, default=False)
    useApis = Column(Boolean, default=False)
    userAuth = Column(Boolean, default=False)
    intensiveTesting = Column(Boolean, default=False)
    workerCount = Column(Integer, default=3)
    isComplete = Column(Boolean, default=False)
    currentStage = Column(String, default="Queued")
    taskPlan = Column(JSON, default=list)
    chatHistory = Column(JSON, default=list)
    uploadedFiles = Column(JSON, default=list)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)
