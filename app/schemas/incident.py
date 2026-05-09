from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    """
    Schema for creating a new incident.
    case_id links this incident to an existing case.
    occurred_at is when the incident happened — separate from created_at
    which is when the record was entered into the system.
    """
    case_id: int
    location: Optional[str] = None
    incident_type: Optional[str] = None
    notes: Optional[str] = None
    occurred_at: Optional[datetime] = None


class IncidentUpdate(BaseModel):
    """All fields optional — only provided fields are updated."""
    location: Optional[str] = None
    incident_type: Optional[str] = None
    notes: Optional[str] = None
    occurred_at: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: int
    case_id: int
    location: Optional[str]
    incident_type: Optional[str]
    notes: Optional[str]
    occurred_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True