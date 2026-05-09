from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class ClaimCreate(BaseModel):
    """
    Schema for creating a new claim.
    case_id links this claim to an existing case.
    incident_date is when the incident occurred, not when the claim was filed.
    """
    case_id: int
    type: Optional[str] = "L"
    incident_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = "Initial"


class ClaimUpdate(BaseModel):
    """
    Schema for updating a claim.
    All fields optional — only provided fields are updated.
    """
    type: Optional[str] = None
    incident_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ClaimResponse(BaseModel):
    id: int
    case_id: int
    type: str
    incident_date: Optional[date]
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True