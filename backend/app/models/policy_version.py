"""
Policy Version model for tracking policy history.

Stores historical snapshots of policies for audit and rollback purposes.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, DateTime, ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base


class PolicyVersion(Base):
    """
    Stores historical versions of policies.
    
    Each time a policy is updated, a new version is created.
    This allows for:
    - Complete audit trail of policy changes
    - Rollback to previous versions
    - Compliance reporting
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
