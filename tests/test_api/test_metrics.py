"""
Tests for Prometheus metrics endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.core.config import settings


def test_metrics_endpoint_exists(client: TestClient) -> None:
    """Test that /metrics endpoint exists and returns Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_metrics_endpoint_returns_prometheus_format(client: TestClient) -> None:
    """Test that /metrics endpoint returns valid Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    
    # Check for standard Prometheus metrics
    assert "python_info" in content or "process_" in content


def test_metrics_endpoint_records_requests(client: TestClient) -> None:
    """Test that metrics endpoint records HTTP requests."""
    # Make a request to generate metrics
    client.get("/")
    
    # Check metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    
    # Should have some HTTP metrics
    assert "http_request" in content or "fastapi" in content


def test_custom_metrics_after_policy_evaluation(
    client: TestClient, admin_token_headers: dict
) -> None:
    """Test that custom metrics are recorded after policy evaluation."""
    # Create agent and policy
    agent_data = {"name": "Metrics Test Agent", "description": "Desc"}
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

    # Make a policy evaluation
    check_data = {"agent_id": agent_id, "resource": "github", "action": "read"}
    client.post(f"{settings.API_V1_STR}/audit/check-permission", json=check_data)

    # Check metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    
    # Should have custom metrics
    assert "agentiam_" in content
