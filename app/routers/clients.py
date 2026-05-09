from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth import validate_api_key
from app.models.client import Client
from app.models.case import Case
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

# APIRouter groups related endpoints together.
# The prefix means all routes here are under /clients automatically.
# The dependency means every route in this router requires a valid API key.
router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(validate_api_key)],
)


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    """
    Create a new client.
    Checks for duplicate email before inserting.
    """
    if client_in.email:
        existing = db.query(Client).filter(Client.email == client_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A client with email {client_in.email} already exists.",
            )

    client = Client(**client_in.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/", response_model=List[ClientResponse])
def list_clients(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    List all clients with basic pagination.
    skip and limit map directly to SQL OFFSET and LIMIT.
    Default limit of 50 prevents accidentally returning 500K records at once.
    """
    return db.query(Client).offset(skip).limit(limit).all()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a single client by ID."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found.",
        )
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int, client_in: ClientUpdate, db: Session = Depends(get_db)
):
    """
    Partially update a client.
    Only fields included in the request body are updated —
    omitted fields are left unchanged.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found.",
        )

    # exclude_unset=True means only fields explicitly sent in the request
    # are included — prevents overwriting existing data with None
    updates = client_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """
    Delete a client by ID.
    Returns 204 No Content on success — no response body.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found.",
        )
    
    # Check for dependent cases before deleting
    case = db.query(Case).filter(Case.case_id == client_id).first()
    if case:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete client {client_id} — it still has cases. Delete cases first.",
        )
    
    db.delete(client)
    db.commit()
