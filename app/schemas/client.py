from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ClientCreate(BaseModel):
    """
    Schema for creating a new client.
    This is what the API expects in the request body.
    Pydantic validates these fields automatically — if first_name is missing,
    FastAPI returns a 422 before your route handler even runs.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class ClientUpdate(BaseModel):
    """
    Schema for updating a client.
    All fields are optional — only provided fields will be updated.
    This is a PATCH pattern rather than PUT (no need to send the full object).
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ClientResponse(BaseModel):
    """
    Schema for the API response when returning a client.
    Controls exactly what fields are exposed — for example, we could
    hide internal fields here if needed.
    """
    id: int
    first_name: str
    last_name: str
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read SQLAlchemy model attributes