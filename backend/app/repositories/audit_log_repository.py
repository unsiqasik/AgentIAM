from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogCreate


class AuditLogRepository:
    def get(self, db: Session, id: int) -> Optional[AuditLog]:
        return db.query(AuditLog).filter(AuditLog.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return (
            db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_agent(
        self, db: Session, agent_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        return (
            db.query(AuditLog)
            .filter(AuditLog.agent_id == agent_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filtered(
        self,
        db: Session,
        *,
        agent_id: Optional[int] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        decision: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Query audit logs with optional filters for agent_id, resource, action, and decision."""
        filters = []
        if agent_id is not None:
            filters.append(AuditLog.agent_id == agent_id)
        if resource is not None:
            filters.append(AuditLog.resource == resource)
        if action is not None:
            filters.append(AuditLog.action == action)
        if decision is not None:
            filters.append(AuditLog.decision == decision)

        query = db.query(AuditLog)
        if filters:
            query = query.filter(and_(*filters))

        return (
            query.order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: AuditLogCreate) -> AuditLog:
        db_obj = AuditLog(
            agent_id=obj_in.agent_id,
            resource=obj_in.resource,
            action=obj_in.action,
            decision=obj_in.decision,
            reason=obj_in.reason,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


audit_log_repository = AuditLogRepository()
