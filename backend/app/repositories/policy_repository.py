from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate


class PolicyRepository:
    def get(self, db: Session, id: int) -> Optional[Policy]:
        return db.query(Policy).filter(Policy.id == id).first()

    def get_by_agent_id(self, db: Session, agent_id: int) -> Optional[Policy]:
        return db.query(Policy).filter(Policy.agent_id == agent_id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Policy]:
        return db.query(Policy).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: PolicyCreate) -> Policy:
        db_obj = Policy(agent_id=obj_in.agent_id, policy_yaml=obj_in.policy_yaml)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Policy, obj_in: PolicyUpdate) -> Policy:
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

    def remove(self, db: Session, *, id: int) -> Policy:
        obj = db.get(Policy, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj  # type: ignore[return-value]


policy_repository = PolicyRepository()
