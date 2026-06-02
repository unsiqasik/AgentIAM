from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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

    class Config:
        from_attributes = True


class CheckPermissionRequest(BaseModel):
    agent_id: int
    resource: str
    action: str
    ip_address: Optional[str] = None


class CheckPermissionResponse(BaseModel):
    allowed: bool
    reason: str
