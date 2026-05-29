from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None

class AgentInDBBase(AgentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Agent(AgentInDBBase):
    pass
