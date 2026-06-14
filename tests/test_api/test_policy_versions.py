"""
Tests for Policy Versioning API endpoints.
"""

from fastapi.testclient import TestClient
from app.core.config import settings


def test_get_policy_versions_empty(
    client: TestClient, admin_token_headers: dict
) -> None:
    """Test getting versions for a non-existent policy."""
    response = client.get(
        f"{settings.API_V1_STR}/policies/999/versions",
        headers=admin_token_headers,
    )
    assert response.status_code == 404


def test_policy_versioning_flow(client: TestClient, admin_token_headers: dict) -> None:
    """Test complete policy versioning flow."""
    # First create an agent
    agent_data = {"name": "Version Test Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    # Create initial policy
    policy_yaml = "permissions: {github: {read: true}}"
    policy_res = client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )
    assert policy_res.status_code == 200
    policy_id = policy_res.json()["id"]

    # Get versions - should have initial version
    versions_res = client.get(
        f"{settings.API_V1_STR}/policies/{policy_id}/versions",
        headers=admin_token_headers,
    )
    assert versions_res.status_code == 200
    versions = versions_res.json()
    assert len(versions) >= 1

    # Update policy
    updated_yaml = "permissions: {github: {read: true, write: true}}"
    update_res = client.put(
        f"{settings.API_V1_STR}/policies/{policy_id}",
        headers=admin_token_headers,
        json={"policy_yaml": updated_yaml},
    )
    assert update_res.status_code == 200

    # Get versions again - should have more versions
    versions_res = client.get(
        f"{settings.API_V1_STR}/policies/{policy_id}/versions",
        headers=admin_token_headers,
    )
    assert versions_res.status_code == 200
    versions = versions_res.json()
    assert len(versions) >= 2


def test_get_specific_version(client: TestClient, admin_token_headers: dict) -> None:
    """Test getting a specific version."""
    # Create agent and policy
    agent_data = {"name": "Specific Version Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    policy_yaml = "permissions: {github: {read: true}}"
    policy_res = client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": policy_yaml},
    )
    policy_id = policy_res.json()["id"]

    # Get version 1
    version_res = client.get(
        f"{settings.API_V1_STR}/policies/{policy_id}/versions/1",
        headers=admin_token_headers,
    )
    assert version_res.status_code == 200
    version = version_res.json()
    assert version["version"] == 1


def test_rollback_policy(client: TestClient, admin_token_headers: dict) -> None:
    """Test rolling back a policy."""
    # Create agent and policy
    agent_data = {"name": "Rollback Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    # Create initial policy
    initial_yaml = "permissions: {github: {read: true}}"
    policy_res = client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": initial_yaml},
    )
    policy_id = policy_res.json()["id"]

    # Update policy
    updated_yaml = "permissions: {github: {read: true, write: true}}"
    client.put(
        f"{settings.API_V1_STR}/policies/{policy_id}",
        headers=admin_token_headers,
        json={"policy_yaml": updated_yaml},
    )

    # Rollback to version 1
    rollback_res = client.post(
        f"{settings.API_V1_STR}/policies/{policy_id}/rollback",
        headers=admin_token_headers,
        json={"version": 1, "change_reason": "Rollback to initial version"},
    )
    assert rollback_res.status_code == 200
    rolled_back = rollback_res.json()
    assert rolled_back["policy_yaml"] == initial_yaml


def test_version_diff(client: TestClient, admin_token_headers: dict) -> None:
    """Test getting diff between versions."""
    # Create agent and policy
    agent_data = {"name": "Diff Agent", "description": "Desc"}
    agent_res = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=agent_data
    )
    agent_id = agent_res.json()["id"]

    # Create initial policy
    initial_yaml = "permissions: {github: {read: true}}"
    policy_res = client.post(
        f"{settings.API_V1_STR}/policies/",
        headers=admin_token_headers,
        json={"agent_id": agent_id, "policy_yaml": initial_yaml},
    )
    policy_id = policy_res.json()["id"]

    # Update policy
    updated_yaml = "permissions: {github: {read: true, write: true}}"
    client.put(
        f"{settings.API_V1_STR}/policies/{policy_id}",
        headers=admin_token_headers,
        json={"policy_yaml": updated_yaml},
    )

    # Get diff between version 1 and 2
    diff_res = client.get(
        f"{settings.API_V1_STR}/policies/{policy_id}/diff/1/2",
        headers=admin_token_headers,
    )
    assert diff_res.status_code == 200
    diff = diff_res.json()
    assert diff["changed"] is True
