from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, func
from app.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    type = Column(String, nullable=True, default="L")
    incident_date = Column(Date, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Initial")
    created_at = Column(DateTime(timezone=True), server_default=func.now())