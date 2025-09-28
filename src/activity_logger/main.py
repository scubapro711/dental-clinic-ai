"""
Component 2.1: Activity Logger Backend (Fixed)

This version resolves the SQLAlchemy reserved name conflict by renaming the
`metadata` field to `activity_metadata` throughout the module.
"""

import os
from datetime import datetime
from typing import List, Optional, Any, Dict

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# --- Database Configuration ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test_activity_logger.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Database Model (Fixed) ---
class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(String, unique=True, index=True, nullable=False)
    agent_id = Column(String, index=True, nullable=False)
    activity_type = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float, nullable=True)
    activity_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata'

# Create the database tables
Base.metadata.create_all(bind=engine)

# --- Pydantic Data Models (Fixed) ---
class ActivityLogIn(BaseModel):
    activity_id: str
    agent_id: str
    activity_type: str
    title: str
    description: str
    confidence_score: Optional[float] = None
    activity_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata'

class ActivityLogOut(ActivityLogIn):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# --- Dependency for Database Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Router ---
router = APIRouter()

@router.post("/log", response_model=ActivityLogOut)
def create_activity_log(activity: ActivityLogIn, db: Session = Depends(get_db)):
    """Receives and stores a new agent activity log."""
    # Pydantic model's 'activity_metadata' now maps directly to the DB model's column
    db_activity = AgentActivityLog(**activity.dict(), timestamp=datetime.utcnow())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.get("/logs/{agent_id}", response_model=List[ActivityLogOut])
def get_agent_logs(agent_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves activity logs for a specific agent."""
    logs = db.query(AgentActivityLog).filter(AgentActivityLog.agent_id == agent_id).offset(skip).limit(limit).all()
    return logs

# --- Main App ---
app = FastAPI(title="Activity Logger Service", version="1.0.1")
app.include_router(router, prefix="/activities")

