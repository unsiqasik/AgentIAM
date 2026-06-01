from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLog(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True, precision=6), server_default=func.now()
    )
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
