import secrets
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.api_key import ApiKey
from app.middleware.auth import validate_api_key, hash_key
from app.routers import clients, cases

app = FastAPI(
    title="Legal Case Management API",
    description="A REST API for managing clients, cases, claims, and partner integrations.",
    version="0.1.0",
)

# Routers
app.include_router(clients.router)
app.include_router(cases.router)

@app.get("/health")
def health_check():
    """Health check — confirms the app is running."""
    return {"status": "ok"}


@app.post("/api-keys")
def create_api_key(partner_name: str, db: Session = Depends(get_db)):
    """
    Generates a new API key for a partner.
    """
    raw_key = secrets.token_urlsafe(32)
    hashed = hash_key(raw_key)

    api_key = ApiKey(partner_name=partner_name, key_hash=hashed)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "partner_name": api_key.partner_name,
        "api_key": raw_key,
        "message": "Save this key — it will not be shown again.",
    }


@app.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    api_key=Depends(validate_api_key),
):
    """Revokes an API key by setting is_active to False."""
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found.")
    key.is_active = False
    db.commit()
    return {"message": f"API key {key_id} revoked."}


@app.get("/validate")
def validate(api_key=Depends(validate_api_key)):
    """
    Validate API Key
    """
    return {"message": f"Authenticated as: {api_key.partner_name}"}