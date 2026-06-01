from fastapi import APIRouter
from app.api.v1.endpoints import login, agents, policies, audit, audit_integrity

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(audit_integrity.router, prefix="/audit/integrity", tags=["audit-integrity"])
