from fastapi.testclient import TestClient
from app.core.config import settings

def test_create_agent(client: TestClient, admin_token_headers: dict) -> None:
    data = {"name": "Test Agent", "description": "A test agent"}
    response = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["description"] == data["description"]
    assert "id" in content

def test_read_agents(client: TestClient, admin_token_headers: dict) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_read_agent(client: TestClient, admin_token_headers: dict) -> None:
    # First create an agent
    data = {"name": "Read Agent", "description": "Agent to be read"}
    create_response = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=data
    )
    agent_id = create_response.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/agents/{agent_id}", headers=admin_token_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == data["name"]

def test_update_agent(client: TestClient, admin_token_headers: dict) -> None:
    # First create an agent
    data = {"name": "Update Agent", "description": "Original desc"}
    create_response = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=data
    )
    agent_id = create_response.json()["id"]

    update_data = {"name": "Updated Agent Name", "description": "Updated desc"}
    response = client.put(
        f"{settings.API_V1_STR}/agents/{agent_id}", headers=admin_token_headers, json=update_data
    )
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

def test_delete_agent(client: TestClient, admin_token_headers: dict) -> None:
    # First create an agent
    data = {"name": "Delete Agent", "description": "To be deleted"}
    create_response = client.post(
        f"{settings.API_V1_STR}/agents/", headers=admin_token_headers, json=data
    )
    agent_id = create_response.json()["id"]

    response = client.delete(
        f"{settings.API_V1_STR}/agents/{agent_id}", headers=admin_token_headers
    )
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(
        f"{settings.API_V1_STR}/agents/{agent_id}", headers=admin_token_headers
    )
    assert get_response.status_code == 404
