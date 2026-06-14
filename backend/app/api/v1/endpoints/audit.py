from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.repositories.audit_log_repository import audit_log_repository
from app.services.authz_service import authz_service
from app.schemas.audit import AuditLog, CheckPermissionRequest, CheckPermissionResponse

router = APIRouter()


@router.get("/", response_model=List[AuditLog])
def read_audit_logs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[int] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve audit logs.
    """
    if agent_id:
        return audit_log_repository.get_by_agent(
            db, agent_id=agent_id, skip=skip, limit=limit
        )
    return audit_log_repository.get_multi(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=AuditLog)
def read_audit_log_by_id(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get audit log by ID.
    """
    audit_log = audit_log_repository.get(db, id=id)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log


@router.post("/check-permission", response_model=CheckPermissionResponse)
def check_permission(
    *,
    db: Session = Depends(deps.get_db),
    request: CheckPermissionRequest,
) -> Any:
    """
    Check if an agent is allowed to perform an action on a resource.
    Note: This endpoint can be used by Agents directly or through a gateway.
    It does not require JWT auth but could be secured with API Keys in the future.
    For MVP, we allow open access for demonstration.
    """
    allowed, reason, is_dry_run = authz_service.check_permission(
        db, agent_id=request.agent_id, resource=request.resource, action=request.action
    allowed, reason = authz_service.check_permission(
        db,
        agent_id=request.agent_id,
        resource=request.resource,
        action=request.action,
        ip_address=request.ip_address,
    )
    return CheckPermissionResponse(allowed=allowed, reason=reason, dry_run=is_dry_run)
