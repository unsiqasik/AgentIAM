"""
Tests for OPA Client
"""

from unittest.mock import MagicMock, patch
import requests
from app.services.opa_client import OPAClient


def test_opa_client_initialization():
    """Test OPA client initialization."""
    client = OPAClient()
    assert client.base_url == "http://localhost:8181"

    client = OPAClient("http://opa.example.com:8181")
    assert client.base_url == "http://opa.example.com:8181"


@patch("app.services.opa_client.requests.Session")
def test_check_permission_success(mock_session_class):
    """Test successful permission check."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_response = MagicMock()
    mock_response.json.return_value = {"result": True}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    client = OPAClient()
    result = client.check_permission("agent1", "github", "read")

    assert result is True
    mock_session.post.assert_called_once()


@patch("app.services.opa_client.requests.Session")
def test_check_permission_denied(mock_session_class):
    """Test denied permission check."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_response = MagicMock()
    mock_response.json.return_value = {"result": False}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    client = OPAClient()
    result = client.check_permission("agent1", "github", "write")

    assert result is False


@patch("app.services.opa_client.requests.Session")
def test_check_permission_error(mock_session_class):
    """Test permission check with error."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_session.post.side_effect = requests.exceptions.RequestException("Connection error")

    client = OPAClient()
    result = client.check_permission("agent1", "github", "read")

    assert result is False


@patch("app.services.opa_client.requests.Session")
def test_get_permissions(mock_session_class):
    """Test getting permissions."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_response = MagicMock()
    mock_response.json.return_value = {"result": ["github", "database"]}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response

    client = OPAClient()
    result = client.get_permissions("agent1")

    assert "github" in result
    assert "database" in result


@patch("app.services.opa_client.requests.Session")
def test_health_check(mock_session_class):
    """Test health check."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_session.get.return_value = mock_response

    client = OPAClient()
    result = client.health_check()

    assert result is True


@patch("app.services.opa_client.requests.Session")
def test_health_check_failure(mock_session_class):
    """Test health check failure."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")

    client = OPAClient()
    result = client.health_check()

    assert result is False
