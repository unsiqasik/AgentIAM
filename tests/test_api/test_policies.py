from fastapi.testclient import TestClient
from app.core.config import settings


def test_create_policy(client: TestClient, admin_token_headers: dict) -> None:
    # Create agent first
    agent_data = {"name": "Policy Test Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = """
permissions:
  github:
    read: true
    write: false
"""
    data = {"agent_id": agent_id, "policy_yaml": policy_yaml}
    response = client.post(
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json=data
    )
    assert response.status_code == 200
    assert response.json()["agent_id"] == agent_id
    assert response.json()["policy_yaml"] == policy_yaml


def test_create_invalid_yaml_policy(
    client: TestClient, admin_token_headers: dict
) -> None:
    # Create agent first
    agent_data = {"name": "Invalid YAML Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "invalid: yaml: : "
    data = {"agent_id": agent_id, "policy_yaml": policy_yaml}
    response = client.post(
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json=data
    )
    assert response.status_code == 400
    assert "Invalid YAML format" in response.json()["detail"]


def test_update_policy(client: TestClient, admin_token_headers: dict) -> None:
    # Create agent and policy
    agent_data = {"name": "Policy Update Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {res: {act: true}}"
    create_res = client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )
    policy_id = create_res.json()["id"]

    new_yaml = "permissions: {res: {act: false}}"
    response = client.put(
        f"{settings.API_V1_STR}/policies/{policy_id}",
        headers=admin_token_headers,
        json={"policy_yaml": new_yaml},
    )
    assert response.status_code == 200
    assert response.json()["policy_yaml"] == new_yaml


def test_create_policy_empty_permissions(
    client: TestClient, admin_token_headers: dict
) -> None:
    # Create agent first
    agent_data = {"name": "Empty Permissions Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {}"
    data = {"agent_id": agent_id, "policy_yaml": policy_yaml}
    response = client.post(
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json=data
    )
    assert response.status_code == 400
    assert "Policy must contain at least one resource" in response.json()["detail"]


def test_create_policy_invalid_permissions_structure(
    client: TestClient, admin_token_headers: dict
) -> None:
    # Create agent first
    agent_data = {"name": "Invalid Struct Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    # permissions should be a dict, not a list
    policy_yaml = "permissions: [resource1]"
    data = {"agent_id": agent_id, "policy_yaml": policy_yaml}
    response = client.post(
        f"{settings.API_V1_STR}/policies/", headers=admin_token_headers, json=data
    )
    assert response.status_code == 400
    assert "'permissions' must be a YAML object" in response.json()["detail"]
