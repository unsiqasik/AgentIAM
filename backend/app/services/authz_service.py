import yaml
from typing import Tuple
from sqlalchemy.orm import Session
from app.repositories.policy_repository import policy_repository
from app.repositories.audit_log_repository import audit_log_repository
from app.schemas.audit import AuditLogCreate


class AuthzService:
    def check_permission(
        self, db: Session, agent_id: int, resource: str, action: str
    ) -> Tuple[bool, str, bool]:
        """Check permission for an agent. Returns (allowed, reason, dry_run)."""
        # 1. Get policy for agent
        policy_obj = policy_repository.get_by_agent_id(db, agent_id=agent_id)

        decision = False
        reason = "Permission not granted"
        is_dry_run = False

        if not policy_obj:
            reason = "No policy found for this agent"
        else:
            is_dry_run = policy_obj.dry_run

            try:
                policy_data = yaml.safe_load(policy_obj.policy_yaml)
                permissions = policy_data.get("permissions", {})

                # Check for resource-level wildcard
                if permissions.get("*") is True:
                    decision = True
                    reason = "Wildcard resource permission granted"
                elif resource in permissions:
                    resource_perms = permissions[resource]

                    # Check if resource perms is a boolean (grant all)
                    if resource_perms is True:
                        decision = True
                        reason = f"Full access granted to resource: {resource}"
                    # Check if resource perms is a dict (fine-grained)
                    elif isinstance(resource_perms, dict):
                        # Check for exact action match first (explicit allow/deny takes precedence over wildcard)
                        if resource_perms.get(action) is True:
                            decision = True
                            reason = f"Permission granted for action: {action} on resource: {resource}"
                        elif resource_perms.get(action) is False:
                            decision = False
                            reason = f"Permission explicitly denied for action: {action} on resource: {resource}"
                        # Check for action-level wildcard
                        elif resource_perms.get("*") is True:
                            decision = True
                            reason = f"Wildcard action permission granted for resource: {resource}"

            except Exception as e:
                decision = False
                reason = f"Error evaluating policy: {str(e)}"

        # 2. In dry run mode, always ALLOW but record what the real decision would be
        if is_dry_run:
            actual_decision = decision
            actual_reason = reason
            decision = True
            reason = f"[DRY RUN] Would {'allow' if actual_decision else 'deny'}: {actual_reason}"

        # 3. Log decision to audit trail
        audit_in = AuditLogCreate(
            agent_id=agent_id,
            resource=resource,
            action=action,
            decision=decision,
            reason=reason,
            dry_run=is_dry_run,
        )
        audit_log_repository.create(db, obj_in=audit_in)

        return decision, reason, is_dry_run


authz_service = AuthzService()
