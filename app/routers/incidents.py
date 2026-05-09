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
    Create a new incident.
    Incidents are all the details around an accident.
    There would be one case per injured defendant under each Incident.
    Returning clients can open a new incident and case.
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
    
    # Check for dependent cases before deleting
    case = db.query(Case).filter(Case.incident_id == incident_id).first()
    if case:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete incident {incident_id} — it still has cases. Delete cases first.",
        )
    
    db.delete(incident)
    db.commit()