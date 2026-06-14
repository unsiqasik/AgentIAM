"""
Tests for Slack notification service.
"""

from unittest.mock import patch, MagicMock
from app.services.slack_service import SlackService


def test_slack_service_initialization():
    """Test Slack service initialization with default values."""
    with patch.dict(
        "os.environ",
        {
            "SLACK_NOTIFICATIONS_ENABLED": "false",
            "SLACK_CRITICAL_RESOURCES": "admin,policies",
            "SLACK_CRITICAL_ACTIONS": "delete,modify",
        },
    ):
        service = SlackService()
        assert service.enabled is False
        assert "admin" in service.critical_resources
        assert "policies" in service.critical_resources
        assert "delete" in service.critical_actions
        assert "modify" in service.critical_actions


def test_is_critical_denial_with_critical_resource():
    """Test critical denial detection with critical resource."""
    with patch.dict(
        "os.environ",
        {
            "SLACK_CRITICAL_RESOURCES": "admin,policies",
            "SLACK_CRITICAL_ACTIONS": "delete,modify",
        },
    ):
        service = SlackService()

        # Critical resource denial
        assert (
            service.is_critical_denial(resource="admin", action="read", decision=False)
            is True
        )

        # Non-critical resource denial
        assert (
            service.is_critical_denial(resource="github", action="read", decision=False)
            is False
        )


def test_is_critical_denial_with_critical_action():
    """Test critical denial detection with critical action."""
    with patch.dict(
        "os.environ",
        {
            "SLACK_CRITICAL_RESOURCES": "admin,policies",
            "SLACK_CRITICAL_ACTIONS": "delete,modify",
        },
    ):
        service = SlackService()

        # Critical action denial
        assert (
            service.is_critical_denial(
                resource="github", action="delete", decision=False
            )
            is True
        )

        # Non-critical action denial
        assert (
            service.is_critical_denial(resource="github", action="read", decision=False)
            is False
        )


def test_is_critical_denial_with_allowed_decision():
    """Test that allowed decisions are not critical denials."""
    with patch.dict(
        "os.environ",
        {
            "SLACK_CRITICAL_RESOURCES": "admin,policies",
            "SLACK_CRITICAL_ACTIONS": "delete,modify",
        },
    ):
        service = SlackService()

        # Allowed decision
        assert (
            service.is_critical_denial(resource="admin", action="delete", decision=True)
            is False
        )


def test_send_denial_notification_disabled():
    """Test notification sending when disabled."""
    with patch.dict("os.environ", {"SLACK_NOTIFICATIONS_ENABLED": "false"}):
        service = SlackService()

        result = service.send_denial_notification(
            agent_id=1, resource="admin", action="delete"
        )

        assert result is False


def test_send_denial_notification_no_config():
    """Test notification sending without configuration."""
    with patch.dict(
        "os.environ",
        {
            "SLACK_NOTIFICATIONS_ENABLED": "true",
            "SLACK_WEBHOOK_URL": "",
            "SLACK_BOT_TOKEN": "",
        },
    ):
        service = SlackService()

        result = service.send_denial_notification(
            agent_id=1, resource="admin", action="delete"
        )

        assert result is False


@patch("app.services.slack_service.requests.post")
def test_send_denial_notification_webhook(mock_post):
    """Test notification sending via webhook."""
    mock_post.return_value = MagicMock(status_code=200)

    with patch.dict(
        "os.environ",
        {
            "SLACK_NOTIFICATIONS_ENABLED": "true",
            "SLACK_WEBHOOK_URL": "https://hooks.slack.com/test",
            "SLACK_CHANNEL": "#test-alerts",
        },
    ):
        service = SlackService()

        result = service.send_denial_notification(
            agent_id=1,
            resource="admin",
            action="delete",
            reason="Unauthorized access attempt",
        )

        assert result is True
        mock_post.assert_called_once()


@patch("app.services.slack_service.WebClient")
def test_send_denial_notification_bot_token(mock_client_class):
    """Test notification sending via bot token."""
    mock_client = MagicMock()
    mock_client.chat_postMessage.return_value = {"ok": True}
    mock_client_class.return_value = mock_client

    with patch.dict(
        "os.environ",
        {
            "SLACK_NOTIFICATIONS_ENABLED": "true",
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_CHANNEL": "#test-alerts",
        },
    ):
        service = SlackService()

        result = service.send_denial_notification(
            agent_id=1,
            resource="admin",
            action="delete",
            reason="Unauthorized access attempt",
        )

        assert result is True
        mock_client.chat_postMessage.assert_called_once()
