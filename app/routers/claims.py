from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.auth import validate_api_key
from app.models.claim import Claim
from app.models.case import Case
from app.schemas.claim import ClaimCreate, ClaimUpdate, ClaimResponse

router = APIRouter(
    prefix="/claims",
    tags=["claims"],
    dependencies=[Depends(validate_api_key)],
)


@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
def create_claim(claim_in: ClaimCreate, db: Session = Depends(get_db)):
    """
    File a new claim against an existing case.

    Two validations before creating:
    1. The case must exist
    2. The case must be open — filing a claim against a closed case isn't allowed.
       This enforces a real business rule: work on a case before it's resolved.
    """
    case = db.query(Case).filter(Case.id == claim_in.case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {claim_in.case_id} not found.",
        )

    if case.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot file a claim against closed case {claim_in.case_id}.",
        )

    claim = Claim(**claim_in.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@router.get("/", response_model=List[ClaimResponse])
def list_claims(
    skip: int = 0,
    limit: int = 50,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List claims with optional filtering by case_id.
    Example: GET /claims?case_id=1 returns all claims for case 1.
    """
    query = db.query(Claim)
    if case_id:
        query = query.filter(Claim.case_id == case_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    """Get a single claim by ID."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found.",
        )
    return claim


@router.patch("/{claim_id}", response_model=ClaimResponse)
def update_claim(
    claim_id: int, claim_in: ClaimUpdate, db: Session = Depends(get_db)
):
    """Partially update a claim."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found.",
        )

    updates = claim_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(claim, field, value)

    db.commit()
    db.refresh(claim)
    return claim


@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    """Delete a claim by ID."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found.",
        )
    db.delete(claim)
    db.commit()