from fastapi.testclient import TestClient
from app.core.config import settings


def test_check_permission_allowed(
    client: TestClient, admin_token_headers: dict
) -> None:
    # Create agent and policy
    agent_data = {"name": "Authz Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {github: {read: true}}"
    client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )

    # Check permission
    check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
    response = client.post(
        f"{settings.API_V1_STR}/audit/check-permission", json=check_data
    )
    assert response.status_code == 200
    assert response.json()["allowed"] is True


def test_check_permission_denied(client: TestClient, admin_token_headers: dict) -> None:
    # Create agent and policy
    agent_data = {"name": "Authz Deny Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {github: {write: false}}"
    client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )

    # Check permission
    check_data = {"agent_id": agent_id, "resource": "github", "action": "write"}
    response = client.post(
        f"{settings.API_V1_STR}/audit/check-permission", json=check_data
    )
    assert response.status_code == 200
    assert response.json()["allowed"] is False


def test_read_audit_logs(client: TestClient, admin_token_headers: dict) -> None:
    response = client.get(f"{settings.API_V1_STR}/audit/", headers=admin_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2  # From the two check_permission calls above


def test_audit_log_timestamp_precision(client: TestClient, admin_token_headers: dict) -> None:
    """Verify that audit log timestamps include microsecond precision in ISO 8601 format."""
    # Create agent and trigger an audit log entry
    agent_data = {"name": "Timestamp Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {github: {read: true}}"
    client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )

    # Trigger audit log via check-permission
    check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
    client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)

    # Retrieve audit logs and verify timestamp precision
    response = client.get(f"{settings.API_V1_STR}/audit/", headers=admin_token_headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0

    # Check that timestamps include microsecond precision
    import re
    pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}"
    for log in logs:
        timestamp = log["timestamp"]
        assert "T" in timestamp, "Timestamp should be ISO 8601 format"
        assert re.search(pattern, timestamp), (
            f"Timestamp should include 6-digit microsecond precision: {timestamp}"
        )
