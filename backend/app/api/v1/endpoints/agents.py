from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.repositories.agent_repository import agent_repository
from app.schemas.agent import Agent, AgentCreate, AgentUpdate

router = APIRouter()


@router.get("/", response_model=List[Agent])
def read_agents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve agents.
    """
    agents = agent_repository.get_multi(db, skip=skip, limit=limit)
    return agents


@router.post("/", response_model=Agent)
def create_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: AgentCreate,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Create new agent.
    """
    agent = agent_repository.get_by_name(db, name=agent_in.name)
    if agent:
        raise HTTPException(
            status_code=400,
            detail="The agent with this name already exists in the system.",
        )
    agent = agent_repository.create(db, obj_in=agent_in)
    return agent


@router.get("/{id}", response_model=Agent)
def read_agent_by_id(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get agent by ID.
    """
    agent = agent_repository.get(db, id=id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{id}", response_model=Agent)
def update_agent(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    agent_in: AgentUpdate,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Update an agent.
    """
    agent = agent_repository.get(db, id=id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_repository.update(db, db_obj=agent, obj_in=agent_in)
    return agent


@router.delete("/{id}", response_model=Agent)
def delete_agent(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: Any = Depends(deps.get_current_admin),
) -> Any:
    """
    Delete an agent.
    """
    agent = agent_repository.get(db, id=id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_repository.remove(db, id=id)
    return agent
