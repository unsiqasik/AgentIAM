"""
Policy Versioning Service

Provides:
- Version tracking for policy changes
- Policy history retrieval
- Rollback to previous versions
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.policy import Policy
from app.models.policy_version import PolicyVersion


class PolicyVersionService:
    """Service for managing policy versions."""

    def create_version(
        self,
        db: Session,
        policy: Policy,
        change_reason: Optional[str] = None,
        changed_by: Optional[str] = None,
    ) -> PolicyVersion:
        """
        Create a new version of a policy.

        This should be called before updating the policy to save the current state.
        """
        # Get the next version number
        latest_version = (
            db.query(PolicyVersion)
            .filter(PolicyVersion.policy_id == policy.id)
            .order_by(desc(PolicyVersion.version))
            .first()
        )

        next_version = (latest_version.version + 1) if latest_version else 1

        # Create version snapshot
        version = PolicyVersion(
            policy_id=policy.id,
            version=next_version,
            policy_yaml=policy.policy_yaml,
            change_reason=change_reason,
            changed_by=changed_by,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    def get_versions(
        self, db: Session, policy_id: int, limit: int = 50
    ) -> List[PolicyVersion]:
        """
        Get all versions of a policy.

        Returns versions in reverse chronological order (newest first).
        """
        return (
            db.query(PolicyVersion)
            .filter(PolicyVersion.policy_id == policy_id)
            .order_by(desc(PolicyVersion.version))
            .limit(limit)
            .all()
        )

    def get_version(
        self, db: Session, policy_id: int, version: int
    ) -> Optional[PolicyVersion]:
        """
        Get a specific version of a policy.
        """
        return (
            db.query(PolicyVersion)
            .filter(
                PolicyVersion.policy_id == policy_id, PolicyVersion.version == version
            )
            .first()
        )

    def get_latest_version(
        self, db: Session, policy_id: int
    ) -> Optional[PolicyVersion]:
        """
        Get the latest version of a policy.
        """
        return (
            db.query(PolicyVersion)
            .filter(PolicyVersion.policy_id == policy_id)
            .order_by(desc(PolicyVersion.version))
            .first()
        )

    def rollback_to_version(
        self,
        db: Session,
        policy_id: int,
        version: int,
        change_reason: Optional[str] = None,
        changed_by: Optional[str] = None,
    ) -> Optional[Policy]:
        """
        Rollback a policy to a specific version.

        This creates a new version with the old policy content.
        """
        # Get the target version
        target_version = self.get_version(db, policy_id, version)
        if not target_version:
            return None

        # Get the current policy
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            return None

        # Create a new version with the current state (before rollback)
        self.create_version(
            db,
            policy,
            change_reason=f"Before rollback to version {version}",
            changed_by=changed_by,
        )

        # Update the policy with the target version's content
        policy.policy_yaml = target_version.policy_yaml
        policy.current_version = policy.current_version + 1

        db.commit()
        db.refresh(policy)

        # Create a version entry for the rollback itself
        self.create_version(
            db,
            policy,
            change_reason=change_reason or f"Rollback to version {version}",
            changed_by=changed_by,
        )

        return policy

    def get_version_diff(
        self, db: Session, policy_id: int, version1: int, version2: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the difference between two versions.

        Returns a dictionary with the changes.
        """
        v1 = self.get_version(db, policy_id, version1)
        v2 = self.get_version(db, policy_id, version2)

        if not v1 or not v2:
            return None

        return {
            "version1": {
                "version": v1.version,
                "policy_yaml": v1.policy_yaml,
                "created_at": v1.created_at.isoformat(),
                "change_reason": v1.change_reason,
                "changed_by": v1.changed_by,
            },
            "version2": {
                "version": v2.version,
                "policy_yaml": v2.policy_yaml,
                "created_at": v2.created_at.isoformat(),
                "change_reason": v2.change_reason,
                "changed_by": v2.changed_by,
            },
            "changed": v1.policy_yaml != v2.policy_yaml,
        }


# Singleton instance
policy_version_service = PolicyVersionService()
