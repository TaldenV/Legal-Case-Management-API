import hashlib
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.api_key import ApiKey

# Tells FastAPI to look for the API key in a header called X-API-Key
# This will also show up in the auto-generated /docs UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_key(raw_key: str) -> str:
    """
    Hashes API key using SHA-256.
    """
    return hashlib.sha256(raw_key.encode()).hexdigest()


def validate_api_key(
    raw_key: str = Security(api_key_header),
    db: Session = Depends(get_db),
) -> ApiKey:
    """
    FastAPI dependency that validates the API key on each request.

    Usage: add `api_key: ApiKey = Depends(validate_api_key)` to any route
    that requires authentication.

    Raises 401 if:
    - No key is provided
    - The key doesn't exist in the database
    - The key exists but is inactive (revoked)
    """
    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key in your request headers.",
        )

    # Hash the incoming key and look it up in the database
    hashed = hash_key(raw_key)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == hashed).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been revoked.",
        )

    # Return the ApiKey record so routes can access partner_name if needed
    return api_key