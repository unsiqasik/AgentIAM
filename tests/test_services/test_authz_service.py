import pytest
from sqlalchemy.orm import Session
from app.services.authz_service import authz_service
from app.repositories.agent_repository import agent_repository
from app.repositories.policy_repository import policy_repository
from app.schemas.agent import AgentCreate
from app.schemas.policy import PolicyCreate

def test_wildcard_resource(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Res Agent"))
    policy_yaml = "permissions: {'*': true}"
    policy_repository.create(db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml))
    
    allowed, reason = authz_service.check_permission(db, agent.id, "any_res", "any_act")
    assert allowed is True
    assert "Wildcard resource permission granted" in reason

def test_wildcard_action(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Act Agent"))
    policy_yaml = "permissions: {github: {'*': true}}"
    policy_repository.create(db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml))
    
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "any_act")
    assert allowed is True
    assert "Wildcard action permission granted" in reason

def test_full_resource_access(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Full Res Agent"))
    policy_yaml = "permissions: {github: true}"
    policy_repository.create(db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml))
    
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True
    assert "Full access granted" in reason

def test_explicit_deny(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Explicit Deny Agent"))
    policy_yaml = "permissions: {github: {delete: false, '*': true}}"
    policy_repository.create(db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml))
    
    # delete should be denied despite wildcard
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "delete")
    assert allowed is False
    assert "explicitly denied" in reason
    
    # other actions allowed
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True
