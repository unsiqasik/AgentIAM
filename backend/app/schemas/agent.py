from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AgentBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AgentCreate(AgentBase):
    name: str  # type: ignore[assignment]


class AgentUpdate(AgentBase):
    name: Optional[str] = None


class AgentInDBBase(AgentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Agent(AgentInDBBase):
    pass
