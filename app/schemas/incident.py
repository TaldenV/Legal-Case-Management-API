from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    """
    Schema for creating a new incident.
    """
    location: Optional[str] = None
    incident_type: Optional[str] = None
    notes: Optional[str] = None
    date_of_loss: Optional[datetime] = None


class IncidentUpdate(BaseModel):
    """All fields optional — only provided fields are updated."""
    location: Optional[str] = None
    incident_type: Optional[str] = None
    notes: Optional[str] = None
    date_of_loss: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: int
    location: Optional[str]
    incident_type: Optional[str]
    notes: Optional[str]
    occurred_at: Optional[datetime]
    date_of_loss: datetime

    class Config:
        from_attributes = True