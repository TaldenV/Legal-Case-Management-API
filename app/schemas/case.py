from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CaseCreate(BaseModel):
    """
    Schema for creating a new case.
    client_id links this case to an existing client.
    case_type examples: 'personal_injury', 'workers_comp', 'medical_malpractice'
    """
    client_id: int
    incident_id: int
    case_type: str
    status: Optional[str] = "Initial"


class CaseUpdate(BaseModel):
    """
    Schema for updating a case.
    All fields optional — only provided fields are updated.
    Setting status to 'Closed' will automatically populate closed_at in the route handler.
    """
    case_type: Optional[str] = None
    status: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    client_id: int
    incident_id: int
    case_type: str
    status: str
    opened_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True