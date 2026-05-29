from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class AgentRepository:
    def get(self, db: Session, id: int) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.name == name).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
        return db.query(Agent).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AgentCreate) -> Agent:
        db_obj = Agent(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Agent, obj_in: AgentUpdate) -> Agent:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Agent:
        obj = db.get(Agent, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj  # type: ignore[return-value]


agent_repository = AgentRepository()
