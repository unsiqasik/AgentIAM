"""
Tests for Audit Log Integrity API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.config import settings


def test_verify_chain_empty(client: TestClient, admin_token_headers: dict) -> None:
    """Test chain verification with no entries."""
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/verify",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["entries_checked"] == 0


def test_get_chain_info_empty(client: TestClient, admin_token_headers: dict) -> None:
    """Test chain info with no entries."""
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/info",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 0
    assert data["chain_length"] == 0


def test_verify_entry_not_found(client: TestClient, admin_token_headers: dict) -> None:
    """Test verification of non-existent entry."""
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/verify/99999",
        headers=admin_token_headers,
    )
    assert response.status_code == 404


def test_verify_chain_with_entries(client: TestClient, admin_token_headers: dict) -> None:
    """Test chain verification with entries."""
    # First create an agent and policy to generate audit logs
    agent_data = {"name": "Integrity Test Agent", "description": "Desc"}
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

    # Generate some audit logs
    for i in range(3):
        check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
        client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)

    # Verify the chain
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/verify",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["entries_checked"] >= 3


def test_verify_single_entry(client: TestClient, admin_token_headers: dict) -> None:
    """Test single entry verification."""
    # First create an agent and policy to generate audit logs
    agent_data = {"name": "Entry Test Agent", "description": "Desc"}
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

    # Generate an audit log
    check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
    client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)

    # Get the audit logs
    response = client.get(
        f"{settings.API_V1_STR}/audit/",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0

    # Verify the first entry
    entry_id = logs[0]["id"]
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/verify/{entry_id}",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["entry_id"] == entry_id


def test_get_chain_info_with_entries(client: TestClient, admin_token_headers: dict) -> None:
    """Test chain info with entries."""
    # First create an agent and policy to generate audit logs
    agent_data = {"name": "Chain Info Agent", "description": "Desc"}
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

    # Generate some audit logs
    for i in range(2):
        check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
        client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)

    # Get chain info
    response = client.get(
        f"{settings.API_V1_STR}/audit/integrity/info",
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] >= 2
    assert data["chain_length"] >= 2
    assert data["last_hash"] is not None
