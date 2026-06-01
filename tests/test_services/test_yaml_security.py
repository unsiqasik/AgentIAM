import pytest
from app.services.policy_service import PolicyService, MAX_YAML_NESTING_DEPTH, MAX_YAML_KEYS


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
        """Test that Billion Laughs-style YAML bombs are rejected."""
        # Classic Billion Laughs attack payload
        yaml_str = """
        a: &a ["lol","lol","lol","lol","lol","lol","lol","lol","lol"]
        b: &b [*a,*a,*a,*a,*a,*a,*a,*a,*a]
        c: &c [*b,*b,*b,*b,*b,*b,*b,*b,*b]
        d: &d [*c,*c,*c,*c,*c,*c,*c,*c,*c]
        e: &e [*d,*d,*d,*d,*d,*d,*d,*d,*d]
        f: &f [*e,*e,*e,*e,*e,*e,*e,*e,*e]
        g: &g [*f,*f,*f,*f,*f,*f,*f,*f,*f]
        h: &h [*g,*g,*g,*g,*g,*g,*g,*g,*g]
        permissions:
          test: true
        """
        # Should either fail during parsing (too many keys) or nesting depth check
        with pytest.raises(ValueError):
            policy_service.validate_yaml(yaml_str)

    def test_excessive_nesting_depth(self, policy_service):
        """Test that deeply nested YAML is rejected."""
        # Create deeply nested YAML exceeding MAX_YAML_NESTING_DEPTH
        nested = "test: true"
        for _ in range(MAX_YAML_NESTING_DEPTH + 2):
            nested = f"level:\n  {nested}"

        yaml_str = f"""
        permissions:
          {nested}
        """
        with pytest.raises(ValueError, match="nesting depth"):
            policy_service.validate_yaml(yaml_str)

    def test_too_many_keys(self, policy_service):
        """Test that YAML with too many keys is rejected."""
        # Generate YAML with more keys than MAX_YAML_KEYS
        keys = "\n".join([f"  key{i}: true" for i in range(MAX_YAML_KEYS + 10)])
        yaml_str = f"""
        permissions:
          resource:
        {keys}
        """
        with pytest.raises(ValueError, match="too many keys"):
            policy_service.validate_yaml(yaml_str)

    def test_long_string_rejection(self, policy_service):
        """Test that excessively long strings are rejected."""
        long_string = "a" * 2000  # Exceeds MAX_YAML_STRING_LENGTH (1000)
        yaml_str = f"""
        permissions:
          {long_string}: true
        """
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
