import yaml
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.repositories.policy_repository import policy_repository
from app.schemas.policy import PolicyCreate, PolicyUpdate
from fastapi import HTTPException

# Security limits for YAML parsing
MAX_YAML_NESTING_DEPTH = 10
MAX_YAML_KEYS = 50
MAX_YAML_STRING_LENGTH = 1000


class SafeYAMLLoader(yaml.SafeLoader):
    """Custom YAML loader with resource limits to prevent DoS attacks."""
    pass


def _construct_limited_mapping(loader, node):
    """Construct YAML mapping with depth and key count limits."""
    loader.flatten_mapping(node)
    pairs = loader.construct_pairs(node)

    # Limit total keys
    if len(pairs) > MAX_YAML_KEYS:
        raise ValueError(
            f"YAML document has too many keys ({len(pairs)}). "
            f"Maximum allowed: {MAX_YAML_KEYS}"
        )

    return dict(pairs)


def _construct_limited_string(loader, node):
    """Construct YAML string with length limit."""
    value = loader.construct_scalar(node)
    if len(value) > MAX_YAML_STRING_LENGTH:
        raise ValueError(
            f"YAML string is too long ({len(value)} chars). "
            f"Maximum allowed: {MAX_YAML_STRING_LENGTH}"
        )
    return value


# Register custom constructors
SafeYAMLLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_limited_mapping,
)
SafeYAMLLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_SCALAR_TAG,
    _construct_limited_string,
)


def _check_nesting_depth(data: Any, max_depth: int = MAX_YAML_NESTING_DEPTH, current_depth: int = 0) -> None:
    """Recursively check YAML nesting depth to prevent Billion Laughs-style attacks."""
    if current_depth > max_depth:
        raise ValueError(
            f"YAML nesting depth exceeds maximum ({max_depth}). "
            f"This may indicate a YAML bomb attack."
        )

    if isinstance(data, dict):
        for value in data.values():
            _check_nesting_depth(value, max_depth, current_depth + 1)
    elif isinstance(data, list):
        for item in data:
            _check_nesting_depth(item, max_depth, current_depth + 1)


class PolicyService:
    def validate_yaml(self, policy_yaml: str) -> Dict[str, Any]:
        try:
            # Use custom SafeLoader with resource limits
            data = yaml.load(policy_yaml, Loader=SafeYAMLLoader)

            if not isinstance(data, dict):
                raise ValueError("Policy must be a YAML object")

            # Check nesting depth to prevent YAML bombs
            _check_nesting_depth(data)

            if "permissions" not in data:
                raise ValueError("Policy must contain 'permissions' key")

            permissions = data["permissions"]
            if not isinstance(permissions, dict):
                raise ValueError("'permissions' must be a YAML object")

            if not permissions:
                raise ValueError(
                    "Policy must contain at least one resource in 'permissions'"
                )

            for resource, actions in permissions.items():
                if not isinstance(resource, str):
                    raise ValueError(f"Resource name must be a string: {resource}")

                if not isinstance(actions, (bool, dict)):
                    raise ValueError(
                        f"Permissions for resource '{resource}' must be a boolean or an object"
                    )

                if isinstance(actions, dict):
                    if not actions:
                        raise ValueError(
                            f"Action list for resource '{resource}' cannot be empty"
                        )
                    for action, allowed in actions.items():
                        if not isinstance(action, str):
                            raise ValueError(
                                f"Action name must be a string: {action} in resource '{resource}'"
                            )
                        if not isinstance(allowed, bool):
                            raise ValueError(
                                f"Permission for action '{action}' in resource '{resource}' must be a boolean"
                            )

            return data
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML format: {exc}")

    def create_policy(self, db: Session, *, obj_in: PolicyCreate):
        try:
            self.validate_yaml(obj_in.policy_yaml)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        existing_policy = policy_repository.get_by_agent_id(
            db, agent_id=obj_in.agent_id
        )
        if existing_policy:
            raise HTTPException(
                status_code=400, detail="Policy already exists for this agent"
            )

        return policy_repository.create(db, obj_in=obj_in)

    def update_policy(self, db: Session, *, id: int, obj_in: PolicyUpdate):
        db_obj = policy_repository.get(db, id=id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Policy not found")

        if obj_in.policy_yaml:
            try:
                self.validate_yaml(obj_in.policy_yaml)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        return policy_repository.update(db, db_obj=db_obj, obj_in=obj_in)


policy_service = PolicyService()
