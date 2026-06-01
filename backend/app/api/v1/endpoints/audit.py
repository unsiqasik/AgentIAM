from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.repositories.audit_log_repository import audit_log_repository
from app.services.authz_service import authz_service
from app.schemas.audit import AuditLog, CheckPermissionRequest, CheckPermissionResponse
from app.core.rate_limiter import check_rate_limit

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


@router.post(
    "/check-permission",
    response_model=CheckPermissionResponse,
    dependencies=[Depends(check_rate_limit)],
)
def check_permission(
    *,
    fastapi_request: Request,
    db: Session = Depends(deps.get_db),
    request_body: CheckPermissionRequest,
) -> Any:
    """
    Check if an agent is allowed to perform an action on a resource.
    Rate-limited to prevent brute-force probing.

    Rate limit headers are included in the response:
    - X-RateLimit-Limit: Max requests per window
    - X-RateLimit-Remaining: Requests remaining in current window
    - X-RateLimit-Reset: Unix timestamp when the window resets

    Returns 429 Too Many Requests when the rate limit is exceeded.
    """
    allowed, reason = authz_service.check_permission(
        db,
        agent_id=request_body.agent_id,
        resource=request_body.resource,
        action=request_body.action,
    )

    response = CheckPermissionResponse(allowed=allowed, reason=reason)

    # Add rate limit headers to response if available
    if hasattr(fastapi_request.state, "rate_limit_headers"):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            content=response.model_dump(),
            headers=fastapi_request.state.rate_limit_headers,
        )

    return response
