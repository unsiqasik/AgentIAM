"""
Policy Versioning API endpoints.

Provides:
- Policy version history
- Version retrieval
- Rollback functionality
- Version comparison
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.policy import Policy
from app.services.policy_version_service import policy_version_service

router = APIRouter()


class PolicyVersionResponse(BaseModel):
    """Response for policy version."""

    id: int
    policy_id: int
    version: int
    policy_yaml: str
    change_reason: str = None
    changed_by: str = None
    created_at: str

    class Config:
        from_attributes = True


class PolicyVersionDiffResponse(BaseModel):
    """Response for version diff."""

    version1: dict
    version2: dict
    changed: bool


class RollbackRequest(BaseModel):
    """Request for rollback."""

    version: int
    change_reason: str = None


@router.get("/{policy_id}/versions", response_model=List[PolicyVersionResponse])
def get_policy_versions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    policy_id: int,
    limit: int = 50,
) -> Any:
    """
    Get all versions of a policy.

    Returns versions in reverse chronological order (newest first).
    """
    # Check if policy exists
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    versions = policy_version_service.get_versions(db, policy_id, limit=limit)

    return [
        PolicyVersionResponse(
            id=v.id,
            policy_id=v.policy_id,
            version=v.version,
            policy_yaml=v.policy_yaml,
            change_reason=v.change_reason,
            changed_by=v.changed_by,
            created_at=v.created_at.isoformat(),
        )
        for v in versions
    ]


@router.get("/{policy_id}/versions/{version}", response_model=PolicyVersionResponse)
def get_policy_version(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    policy_id: int,
    version: int,
) -> Any:
    """
    Get a specific version of a policy.
    """
    # Check if policy exists
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    version_obj = policy_version_service.get_version(db, policy_id, version)
    if not version_obj:
        raise HTTPException(status_code=404, detail="Version not found")

    return PolicyVersionResponse(
        id=version_obj.id,
        policy_id=version_obj.policy_id,
        version=version_obj.version,
        policy_yaml=version_obj.policy_yaml,
        change_reason=version_obj.change_reason,
        changed_by=version_obj.changed_by,
        created_at=version_obj.created_at.isoformat(),
    )


@router.post("/{policy_id}/rollback", response_model=PolicyVersionResponse)
def rollback_policy(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    policy_id: int,
    rollback_data: RollbackRequest,
) -> Any:
    """
    Rollback a policy to a specific version.

    This creates a new version with the old policy content.
    """
    # Check if policy exists
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Perform rollback
    rolled_back_policy = policy_version_service.rollback_to_version(
        db,
        policy_id,
        rollback_data.version,
        change_reason=rollback_data.change_reason,
        changed_by=current_user.username,
    )

    if not rolled_back_policy:
        raise HTTPException(status_code=404, detail="Version not found")

    # Get the latest version (the rollback version)
    latest_version = policy_version_service.get_latest_version(db, policy_id)

    return PolicyVersionResponse(
        id=latest_version.id,
        policy_id=latest_version.policy_id,
        version=latest_version.version,
        policy_yaml=latest_version.policy_yaml,
        change_reason=latest_version.change_reason,
        changed_by=latest_version.changed_by,
        created_at=latest_version.created_at.isoformat(),
    )


@router.get(
    "/{policy_id}/diff/{version1}/{version2}", response_model=PolicyVersionDiffResponse
)
def get_version_diff(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    policy_id: int,
    version1: int,
    version2: int,
) -> Any:
    """
    Get the difference between two versions.
    """
    # Check if policy exists
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    diff = policy_version_service.get_version_diff(db, policy_id, version1, version2)
    if not diff:
        raise HTTPException(status_code=404, detail="One or both versions not found")

    return PolicyVersionDiffResponse(**diff)
