from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base_class import Base


class Policy(Base):
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent.id"), unique=True, nullable=False)
    policy_yaml = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
