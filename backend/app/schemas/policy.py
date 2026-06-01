from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PolicyBase(BaseModel):
    agent_id: int
    policy_yaml: str
    expires_at: Optional[datetime] = None


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    policy_yaml: Optional[str] = None
    expires_at: Optional[datetime] = None


class PolicyInDBBase(PolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Policy(PolicyInDBBase):
    pass
