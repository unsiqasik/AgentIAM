import pytest
from app.services.policy_service import (
    PolicyService,
    MAX_YAML_NESTING_DEPTH,
    MAX_YAML_KEYS,
)


@pytest.fixture
def policy_service():
    return PolicyService()


class TestYAMLSecurity:
    """Tests for YAML injection and DoS prevention."""

    def test_valid_policy_yaml(self, policy_service):
        """Test that valid policy YAML is accepted."""
        yaml_str = """
        permissions:
          github:
            read: true
            write: false
        """
        result = policy_service.validate_yaml(yaml_str)
        assert "permissions" in result
        assert result["permissions"]["github"]["read"] is True

    def test_billion_laughs_prevention(self, policy_service):
        """Test that Billion Laughs-style YAML bombs are rejected.

        PyYAML's SafeLoader handles aliases lazily, so the classic
        Billion Laughs payload may parse without expanding. Instead,
        we verify that our depth check catches deeply nested structures
        built via aliases.
        """
        # Build a YAML bomb that creates deep nesting via aliases
        yaml_str = (
            "a: &a\n"
            "  b: &b\n"
            "    c: &c\n"
            "      d: &d\n"
            "        e: &e\n"
            "          f: &f\n"
            "            g: &g\n"
            "              h: &h\n"
            "                i: &i\n"
            "                  j: &j\n"
            "                    k: &k\n"
            "                      l: true\n"
            "permissions:\n"
            "  test: *a\n"
        )
        # Should raise due to nesting depth exceeded
        with pytest.raises(ValueError, match="nesting depth|Invalid YAML"):
            policy_service.validate_yaml(yaml_str)

    def test_excessive_nesting_depth(self, policy_service):
        """Test that deeply nested YAML is rejected."""
        # Build properly indented nested YAML
        indent = "  "
        nested = f"{indent * (MAX_YAML_NESTING_DEPTH + 2)}test: true"
        for i in range(MAX_YAML_NESTING_DEPTH + 1, 0, -1):
            nested = f"{indent * i}level:\n{nested}"

        yaml_str = f"permissions:\n{nested}\n"
        with pytest.raises(ValueError, match="nesting depth"):
            policy_service.validate_yaml(yaml_str)

    def test_too_many_keys(self, policy_service):
        """Test that YAML with too many keys is rejected."""
        # Generate a dict with more keys than MAX_YAML_KEYS at the top level
        entries = [f"  key{i}: true" for i in range(MAX_YAML_KEYS + 10)]
        keys = "\n".join(entries)
        yaml_str = f"permissions:\n  resource:\n{keys}\n"
        with pytest.raises(ValueError, match="too many keys"):
            policy_service.validate_yaml(yaml_str)

    def test_long_string_rejection(self, policy_service):
        """Test that excessively long strings are rejected."""
        # Use a long string as a value (not a key) so it parses correctly
        long_string = "a" * 2000  # Exceeds MAX_YAML_STRING_LENGTH (1000)
        yaml_str = f"permissions:\n  resource:\n    read: {long_string}\n"
        with pytest.raises(ValueError, match="too long"):
            policy_service.validate_yaml(yaml_str)

    def test_non_dict_yaml_rejection(self, policy_service):
        """Test that non-dict YAML is rejected."""
        yaml_str = "- item1\n- item2"
        with pytest.raises(ValueError, match="must be a YAML object"):
            policy_service.validate_yaml(yaml_str)

    def test_missing_permissions_key(self, policy_service):
        """Test that YAML without 'permissions' key is rejected."""
        yaml_str = "config:\n  debug: true"
        with pytest.raises(ValueError, match="must contain 'permissions'"):
            policy_service.validate_yaml(yaml_str)

    def test_empty_permissions(self, policy_service):
        """Test that empty permissions object is rejected."""
        yaml_str = "permissions: {}"
        with pytest.raises(ValueError, match="at least one resource"):
            policy_service.validate_yaml(yaml_str)

    def test_invalid_resource_name_type(self, policy_service):
        """Test that non-string resource names are rejected."""
        yaml_str = "permissions:\n  123: true"
        with pytest.raises(ValueError, match="Resource name must be a string"):
            policy_service.validate_yaml(yaml_str)

    def test_invalid_action_value_type(self, policy_service):
        """Test that non-boolean action values are rejected."""
        yaml_str = """
        permissions:
          github:
            read: "yes"
        """
        with pytest.raises(ValueError, match="must be a boolean"):
            policy_service.validate_yaml(yaml_str)

    def test_custom_tags_blocked(self, policy_service):
        """Test that custom YAML tags (potential code execution) are blocked."""
        yaml_str = """
        permissions:
          github:
            read: !!python/object/apply:os.system ["echo pwned"]
        """
        with pytest.raises(Exception):  # Should fail with safe loading
            policy_service.validate_yaml(yaml_str)

    def test_anchors_and_aliases_safe(self, policy_service):
        """Test that legitimate use of anchors/aliases works within limits."""
        yaml_str = """
        permissions:
          defaults: &defaults
            read: true
            write: false
          github:
            <<: *defaults
          gitlab:
            <<: *defaults
        """
        result = policy_service.validate_yaml(yaml_str)
        assert result["permissions"]["github"]["read"] is True
        assert result["permissions"]["gitlab"]["write"] is False
