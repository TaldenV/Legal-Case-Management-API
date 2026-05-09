from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.auth import validate_api_key
from app.models.case import Case
from app.models.client import Client
from app.models.claim import Claim
from app.models.incident import Incident
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse

router = APIRouter(
    prefix="/cases",
    tags=["cases"],
    dependencies=[Depends(validate_api_key)],
)


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    """
    Open a new case for an existing client.
    Verifies the client exists before creating the case —
    this enforces referential integrity at the application layer,
    on top of the foreign key constraint at the database layer.
    """
    client = db.query(Client).filter(Client.id == case_in.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {case_in.client_id} not found.",
        )

    case = Case(**case_in.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/", response_model=List[CaseResponse])
def list_cases(
    skip: int = 0,
    limit: int = 50,
    client_id: Optional[int] = None,
    incident_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List cases with optional filtering by client_id and/or incident_id.
    Example: GET /cases?client_id=1 returns all cases for client 1.
    This is more useful than always returning every case in the system.
    """
    query = db.query(Case)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    if incident_id:
        query = query.filter(Case.incident_id == incident_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)): 
    """Get a single case by ID."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found.",
        )
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(case_id: int, case_in: CaseUpdate, db: Session = Depends(get_db)):
    """
    Partially update a case.
    Key behavior: if status is set to 'Closed', closed_at is automatically
    set to the current timestamp — the client doesn't need to send it.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found.",
        )

    updates = case_in.model_dump(exclude_unset=True)

    if "status" in updates:
        if updates["status"] == "Closed" and case.status != "Closed":
            case.closed_at = datetime.now(timezone.utc)

    for field, value in updates.items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    """Delete a case by ID."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found.",
        )

    # Check for dependent claims before deleting
    claims = db.query(Claim).filter(Claim.case_id == case_id).first()
    if claims:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete case {case_id} — it still has claims. Delete claims first.",
        )

    db.delete(case)
    db.commit()