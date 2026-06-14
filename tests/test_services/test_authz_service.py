from sqlalchemy.orm import Session
from app.services.authz_service import authz_service
from app.repositories.agent_repository import agent_repository
from app.repositories.policy_repository import policy_repository
from app.schemas.agent import AgentCreate
from app.schemas.policy import PolicyCreate


def test_wildcard_resource(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Res Agent"))
    policy_yaml = "permissions: {'*': true}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason = authz_service.check_permission(db, agent.id, "any_res", "any_act")
    assert allowed is True
    assert "Wildcard resource permission granted" in reason


def test_wildcard_action(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Act Agent"))
    policy_yaml = "permissions: {github: {'*': true}}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason = authz_service.check_permission(db, agent.id, "github", "any_act")
    assert allowed is True
    assert "Wildcard action permission granted" in reason


def test_full_resource_access(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Full Res Agent"))
    policy_yaml = "permissions: {github: true}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True
    assert "Full access granted" in reason


def test_explicit_deny(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Explicit Deny Agent"))
    policy_yaml = "permissions: {github: {delete: false, '*': true}}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    # delete should be denied despite wildcard
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "delete")
    assert allowed is False
    assert "explicitly denied" in reason

    # other actions allowed
    allowed, reason = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True


def test_ip_cidr_restrictions(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="IP Restricted Agent"))
    policy_yaml = """
ip_restrictions:
  allowed_cidrs:
    - 192.168.1.0/24
    - 10.0.0.1/32
permissions:
  '*': true
"""
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    # 1. Allowed IP in range
    allowed, reason = authz_service.check_permission(
        db, agent.id, "res", "act", ip_address="192.168.1.50"
    )
    assert allowed is True

    # 2. Allowed exact IP
    allowed, reason = authz_service.check_permission(
        db, agent.id, "res", "act", ip_address="10.0.0.1"
    )
    assert allowed is True

    # 3. Denied IP
    allowed, reason = authz_service.check_permission(
        db, agent.id, "res", "act", ip_address="192.168.2.1"
    )
    assert allowed is False
    assert "not allowed by policy" in reason

    # 4. Missing IP when required
    allowed, reason = authz_service.check_permission(db, agent.id, "res", "act")
    assert allowed is False
    assert "IP address is required" in reason

    # 5. Invalid IP
    allowed, reason = authz_service.check_permission(
        db, agent.id, "res", "act", ip_address="not-an-ip"
    )
    assert allowed is False
    assert "Invalid IP address" in reason
