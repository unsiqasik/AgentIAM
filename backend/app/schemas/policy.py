from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PolicyBase(BaseModel):
    agent_id: int
    policy_yaml: str
    dry_run: bool = False


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    policy_yaml: Optional[str] = None
    dry_run: Optional[bool] = None


class PolicyInDBBase(PolicyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Policy(PolicyInDBBase):
    pass
