"""
OPA Client for AgentIAM

This module provides a client for interacting with OPA (Open Policy Agent).
It's a prototype for future OPA integration.
"""

import requests
from typing import Dict, Any, Optional


class OPAClient:
    """Client for OPA HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8181"):
        """
        Initialize OPA client.

        Args:
            base_url: OPA server URL (default: http://localhost:8181)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def check_permission(
        self,
        agent_id: str,
        resource: str,
        action: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if an agent has permission to perform an action on a resource.

        Args:
            agent_id: Agent identifier
            resource: Resource to access
            action: Action to perform
            user_id: Optional user identifier for user-based policies
            context: Additional context for policy evaluation

        Returns:
            True if permission granted, False otherwise
        """
        input_data = {"agent_id": agent_id, "resource": resource, "action": action}

        if user_id:
            input_data["user_id"] = user_id

        if context:
            input_data.update(context)

        try:
            response = self.session.post(
                f"{self.base_url}/v1/data/agentiam/allow",
                json={"input": input_data},
                timeout=5,
            )
            response.raise_for_status()

            result = response.json()
            return result.get("result", False)

        except requests.exceptions.RequestException as e:
            # Log error and fall back to deny
            print(f"OPA request failed: {e}")
            return False

    def get_permissions(self, agent_id: str) -> Dict[str, Any]:
        """
        Get all permissions for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Dictionary of permissions
        """
        try:
            response = self.session.post(
                f"{self.base_url}/v1/data/agentiam/permissions",
                json={"input": {"agent_id": agent_id}},
                timeout=5,
            )
            response.raise_for_status()

            result = response.json()
            return result.get("result", {})

        except requests.exceptions.RequestException as e:
            print(f"OPA request failed: {e}")
            return {}

    def has_permissions(self, agent_id: str) -> bool:
        """
        Check if an agent has any permissions defined.

        Args:
            agent_id: Agent identifier

        Returns:
            True if agent has permissions, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.base_url}/v1/data/agentiam/has_permissions",
                json={"input": {"agent_id": agent_id}},
                timeout=5,
            )
            response.raise_for_status()

            result = response.json()
            return result.get("result", False)

        except requests.exceptions.RequestException as e:
            print(f"OPA request failed: {e}")
            return False

    def update_policy(self, policy_data: Dict[str, Any]) -> bool:
        """
        Update OPA policy data.

        Args:
            policy_data: Policy data to upload

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.put(
                f"{self.base_url}/v1/data/policies", json=policy_data, timeout=10
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            print(f"OPA policy update failed: {e}")
            return False

    def get_policy(self) -> Dict[str, Any]:
        """
        Get current OPA policy data.

        Returns:
            Current policy data
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/data/policies", timeout=5)
            response.raise_for_status()

            result = response.json()
            return result.get("result", {})

        except requests.exceptions.RequestException as e:
            print(f"OPA policy retrieval failed: {e}")
            return {}

    def health_check(self) -> bool:
        """
        Check if OPA server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200

        except requests.exceptions.RequestException:
            return False


# Singleton instance
opa_client = OPAClient()
