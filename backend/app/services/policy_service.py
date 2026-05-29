import yaml
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories.policy_repository import policy_repository
from app.schemas.policy import PolicyCreate, PolicyUpdate
from fastapi import HTTPException

class PolicyService:
    def validate_yaml(self, policy_yaml: str) -> Dict[str, Any]:
        try:
            data = yaml.safe_load(policy_yaml)
            if not isinstance(data, dict):
                raise ValueError("Policy must be a YAML object")
            if "permissions" not in data:
                raise ValueError("Policy must contain 'permissions' key")
            
            permissions = data["permissions"]
            if not isinstance(permissions, dict):
                raise ValueError("'permissions' must be a YAML object")
            
            if not permissions:
                raise ValueError("Policy must contain at least one resource in 'permissions'")
            
            for resource, actions in permissions.items():
                if not isinstance(resource, str):
                    raise ValueError(f"Resource name must be a string: {resource}")
                
                if not isinstance(actions, (bool, dict)):
                    raise ValueError(f"Permissions for resource '{resource}' must be a boolean or an object")
                
                if isinstance(actions, dict):
                    if not actions:
                        raise ValueError(f"Action list for resource '{resource}' cannot be empty")
                    for action, allowed in actions.items():
                        if not isinstance(action, str):
                            raise ValueError(f"Action name must be a string: {action} in resource '{resource}'")
                        if not isinstance(allowed, bool):
                            raise ValueError(f"Permission for action '{action}' in resource '{resource}' must be a boolean")
            
            return data
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML format: {exc}")

    def create_policy(self, db: Session, *, obj_in: PolicyCreate):
        try:
            self.validate_yaml(obj_in.policy_yaml)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        existing_policy = policy_repository.get_by_agent_id(db, agent_id=obj_in.agent_id)
        if existing_policy:
            raise HTTPException(status_code=400, detail="Policy already exists for this agent")
            
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
