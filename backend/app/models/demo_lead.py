"""
Demo Lead Model

Stores information about users who try the demo.
Used for lead tracking and conversion analysis.
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base


class DemoLead(Base):
    """
    Demo lead information.
    
    Tracks users who start a demo session.
    """
    __tablename__ = "demo_leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, comment="Lead's full name")
    email = Column(String, nullable=False, comment="Lead's email address")
    phone = Column(String, nullable=False, comment="Lead's phone number")
    created_at = Column(DateTime, default=datetime.utcnow, comment="When demo session was created")
    converted = Column(Boolean, default=False, comment="Did they sign up?")
    converted_at = Column(DateTime, nullable=True, comment="When they signed up")
    
    def __repr__(self):
        return f"<DemoLead(id={self.id}, email={self.email}, converted={self.converted})>"
