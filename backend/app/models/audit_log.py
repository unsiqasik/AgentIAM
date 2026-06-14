from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLog(Base):
    __table_args__ = (Index("ix_audit_log_agent_timestamp", "agent_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Integrity fields for hash chain
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False)
