from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class AuditLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    agent_id = Column(Integer, nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    decision = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)
