"""
Tests for temporary/expiring policies.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from app.services.authz_service import AuthzService


def test_check_permission_with_expired_policy():
    """Test that expired policies are denied."""
    # Create mock policy with expires_at in the past
    policy_obj = MagicMock()
    policy_obj.policy_yaml = "permissions: {github: {read: true}}"
    policy_obj.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

    # Create mock repository
    policy_repository = MagicMock()
    policy_repository.get_by_agent_id.return_value = policy_obj

    # Create mock audit repository
    audit_log_repository = MagicMock()

    # Create service
    service = AuthzService()
    service.policy_repository = policy_repository
    service.audit_log_repository = audit_log_repository

    # Test
    decision, reason = service.check_permission(
        db=MagicMock(), agent_id=1, resource="github", action="read"
    )

    assert decision is False
    assert "expired" in reason.lower()


def test_check_permission_with_active_policy():
    """Test that active policies are allowed."""
    # Create mock policy with expires_at in the future
    policy_obj = MagicMock()
    policy_obj.policy_yaml = "permissions: {github: {read: true}}"
    policy_obj.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # Create mock repository
    policy_repository = MagicMock()
    policy_repository.get_by_agent_id.return_value = policy_obj

    # Create mock audit repository
    audit_log_repository = MagicMock()

    # Create service
    service = AuthzService()
    service.policy_repository = policy_repository
    service.audit_log_repository = audit_log_repository

    # Test
    decision, reason = service.check_permission(
        db=MagicMock(), agent_id=1, resource="github", action="read"
    )

    assert decision is True


def test_check_permission_with_no_expiration():
    """Test that policies without expiration work normally."""
    # Create mock policy without expires_at
    policy_obj = MagicMock()
    policy_obj.policy_yaml = "permissions: {github: {read: true}}"
    policy_obj.expires_at = None

    # Create mock repository
    policy_repository = MagicMock()
    policy_repository.get_by_agent_id.return_value = policy_obj

    # Create mock audit repository
    audit_log_repository = MagicMock()

    # Create service
    service = AuthzService()
    service.policy_repository = policy_repository
    service.audit_log_repository = audit_log_repository

    # Test
    decision, reason = service.check_permission(
        db=MagicMock(), agent_id=1, resource="github", action="read"
    )

    assert decision is True


def test_check_permission_with_no_policy():
    """Test that missing policies are denied."""
    # Create mock repository
    policy_repository = MagicMock()
    policy_repository.get_by_agent_id.return_value = None

    # Create mock audit repository
    audit_log_repository = MagicMock()

    # Create service
    service = AuthzService()
    service.policy_repository = policy_repository
    service.audit_log_repository = audit_log_repository

    # Test
    decision, reason = service.check_permission(
        db=MagicMock(), agent_id=1, resource="github", action="read"
    )

    assert decision is False
    assert "no policy" in reason.lower()
