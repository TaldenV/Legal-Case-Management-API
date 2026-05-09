from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.auth import validate_api_key
from app.models.incident import Incident
from app.models.case import Case
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    dependencies=[Depends(validate_api_key)],
)


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    """
    Record a new incident against an existing case.
    Incidents are factual records of what happened — Case status does not
    gate incident creation since documentation may be needed regardless of
    whether a case is open or closed.
    """
    case = db.query(Case).filter(Case.id == incident_in.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {incident_in.case_id} not found.",
        )

    incident = Incident(**incident_in.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    skip: int = 0,
    limit: int = 50,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List incidents with optional filtering by case_id.
    Example: GET /incidents?case_id=1 returns all incidents for case 1.
    """
    query = db.query(Incident)
    if case_id:
        query = query.filter(Incident.case_id == case_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get a single incident by ID."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int, incident_in: IncidentUpdate, db: Session = Depends(get_db)
):
    """Partially update an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    updates = incident_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    """Delete an incident by ID."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )
    db.delete(incident)
    db.commit()