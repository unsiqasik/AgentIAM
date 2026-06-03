from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_serializer


class AuditLogBase(BaseModel):
    agent_id: int
    resource: str
    action: str
    decision: bool
    reason: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp")
    @staticmethod
    def serialize_timestamp(value: datetime) -> str:
        """Serialize datetime with full microsecond precision in ISO 8601 format."""
        return value.isoformat(timespec="microseconds")


class CheckPermissionRequest(BaseModel):
    agent_id: int
    resource: str
    action: str
    ip_address: Optional[str] = None


class CheckPermissionResponse(BaseModel):
    allowed: bool
    reason: str
