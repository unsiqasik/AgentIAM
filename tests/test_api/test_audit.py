from fastapi.testclient import TestClient
from app.core.config import settings

def test_check_permission_allowed(client: TestClient, admin_token_headers: dict) -> None:
    # Create agent and policy
    agent_data = {"name": "Authz Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {github: {read: true}}"
    client.post(
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json={"agent_id": agent_id, "policy_yaml": policy_yaml}
    )

    # Check permission
    check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
    response = client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)
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
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json={"agent_id": agent_id, "policy_yaml": policy_yaml}
    )

    # Check permission
    check_data = {"agent_id": agent_id, "resource": "github", "action": "write"}
    response = client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)
    assert response.status_code == 200
    assert response.json()["allowed"] is False

def test_read_audit_logs(client: TestClient, admin_token_headers: dict) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/audit/", headers=admin_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2  # From the two check_permission calls above
