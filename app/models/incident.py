from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    location = Column(String, nullable=True)
    incident_type = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())