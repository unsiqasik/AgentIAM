from fastapi import APIRouter
from app.api.v1.endpoints import login, mfa, agents, policies, audit

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(mfa.router, prefix="/mfa", tags=["mfa"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
