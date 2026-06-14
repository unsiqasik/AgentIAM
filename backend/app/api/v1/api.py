from fastapi import APIRouter
from app.api.v1.endpoints import login, agents, policies, audit, policy_versions

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(
    policy_versions.router, prefix="/policies", tags=["policy-versions"]
)
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
