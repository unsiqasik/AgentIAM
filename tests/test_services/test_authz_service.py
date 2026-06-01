from sqlalchemy.orm import Session
from app.services.authz_service import authz_service
from app.repositories.agent_repository import agent_repository
from app.repositories.policy_repository import policy_repository
from app.repositories.audit_log_repository import audit_log_repository
from app.schemas.agent import AgentCreate
from app.schemas.policy import PolicyCreate


def test_wildcard_resource(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Res Agent"))
    policy_yaml = "permissions: {'*': true}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "any_res", "any_act")
    assert allowed is True
    assert "Wildcard resource permission granted" in reason
    assert dry_run is False


def test_wildcard_action(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Wildcard Act Agent"))
    policy_yaml = "permissions: {github: {'*': true}}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "github", "any_act")
    assert allowed is True
    assert "Wildcard action permission granted" in reason


def test_full_resource_access(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Full Res Agent"))
    policy_yaml = "permissions: {github: true}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True
    assert "Full access granted" in reason


def test_explicit_deny(db: Session) -> None:
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Explicit Deny Agent"))
    policy_yaml = "permissions: {github: {delete: false, '*': true}}"
    policy_repository.create(
        db, obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml)
    )

    # delete should be denied despite wildcard
    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "github", "delete")
    assert allowed is False
    assert "explicitly denied" in reason

    # other actions allowed
    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True


def test_dry_run_allows_denied_action(db: Session) -> None:
    """Dry run mode should always return ALLOW, even for denied actions."""
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Dry Run Agent"))
    policy_yaml = "permissions: {github: {delete: false, read: true}}"
    policy_repository.create(
        db,
        obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml, dry_run=True),
    )

    # delete is denied in policy, but dry run should allow it
    allowed, reason, is_dry_run = authz_service.check_permission(db, agent.id, "github", "delete")
    assert allowed is True
    assert is_dry_run is True
    assert "[DRY RUN]" in reason
    assert "Would deny" in reason

    # read is allowed, dry run should still allow it
    allowed, reason, is_dry_run = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is True
    assert is_dry_run is True
    assert "[DRY RUN]" in reason
    assert "Would allow" in reason


def test_dry_run_logs_actual_decision(db: Session) -> None:
    """Dry run should log the actual decision (denied) even though it returns allow."""
    agent = agent_repository.create(db, obj_in=AgentCreate(name="Dry Run Log Agent"))
    policy_yaml = "permissions: {github: {delete: false}}"
    policy_repository.create(
        db,
        obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml, dry_run=True),
    )

    authz_service.check_permission(db, agent.id, "github", "delete")

    # Check audit log — decision should be True (dry run allows) but marked as dry_run
    logs = audit_log_repository.get_by_agent(db, agent_id=agent.id)
    assert len(logs) == 1
    assert logs[0].decision is True  # dry run always allows
    assert logs[0].dry_run is True
    assert "[DRY RUN]" in logs[0].reason


def test_dry_run_off_enforces_policy(db: Session) -> None:
    """With dry_run=False, denied actions should actually be denied."""
    agent = agent_repository.create(db, obj_in=AgentCreate(name="No Dry Run Agent"))
    policy_yaml = "permissions: {github: {delete: false, read: true}}"
    policy_repository.create(
        db,
        obj_in=PolicyCreate(agent_id=agent.id, policy_yaml=policy_yaml, dry_run=False),
    )

    allowed, reason, is_dry_run = authz_service.check_permission(db, agent.id, "github", "delete")
    assert allowed is False
    assert "explicitly denied" in reason
    assert is_dry_run is False

    # Audit log should not be marked as dry_run
    logs = audit_log_repository.get_by_agent(db, agent_id=agent.id)
    assert len(logs) == 1
    assert logs[0].dry_run is False


def test_no_policy_returns_denied(db: Session) -> None:
    """Agent with no policy should be denied."""
    agent = agent_repository.create(db, obj_in=AgentCreate(name="No Policy Agent"))

    allowed, reason, dry_run = authz_service.check_permission(db, agent.id, "github", "read")
    assert allowed is False
    assert "No policy found" in reason
    assert dry_run is False
