from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.repositories.policy_repository import policy_repository
from app.services.policy_service import policy_service
from app.schemas.policy import Policy, PolicyCreate, PolicyUpdate

router = APIRouter()


@router.get("/", response_model=List[Policy])
def read_policies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve policies.
    """
    policies = policy_repository.get_multi(db, skip=skip, limit=limit)
    return policies


@router.post("/", response_model=Policy)
def create_policy(
    *,
    db: Session = Depends(deps.get_db),
    policy_in: PolicyCreate,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new policy.
    """
    return policy_service.create_policy(db, obj_in=policy_in)


@router.get("/{id}", response_model=Policy)
def read_policy_by_id(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get policy by ID.
    """
    policy = policy_repository.get(db, id=id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.get("/agent/{agent_id}", response_model=Policy)
def read_policy_by_agent_id(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get policy by agent ID.
    """
    policy = policy_repository.get_by_agent_id(db, agent_id=agent_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found for this agent")
    return policy


@router.put("/{id}", response_model=Policy)
def update_policy(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    policy_in: PolicyUpdate,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Update a policy.
    """
    return policy_service.update_policy(db, id=id, obj_in=policy_in)


@router.delete("/{id}", response_model=Policy)
def delete_policy(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Delete a policy.
    """
    policy = policy_repository.get(db, id=id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    policy = policy_repository.remove(db, id=id)
    return policy
