"""
Audit Log Integrity Service

Provides cryptographic chaining for audit log entries to detect tampering.

Each audit log entry includes:
- previous_hash: SHA-256 hash of the previous entry
- entry_hash: SHA-256 hash of the current entry (including previous_hash)

This creates a hash chain where any modification to a previous entry
will break the chain and be detectable.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit_log import AuditLog


class AuditIntegrityService:
    """Service for managing audit log integrity through hash chaining."""

    def __init__(self):
        self.algorithm = "sha256"

    def _compute_hash(self, data: str) -> str:
        """Compute SHA-256 hash of the given data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _create_entry_data(self, entry: AuditLog) -> str:
        """
        Create a deterministic string representation of an audit log entry.
        
        This excludes the hash fields themselves to avoid circular dependencies.
        """
        data = {
            "id": entry.id,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
            "agent_id": entry.agent_id,
            "resource": entry.resource,
            "action": entry.action,
            "decision": entry.decision,
            "reason": entry.reason,
            "previous_hash": entry.previous_hash,
        }
        return json.dumps(data, sort_keys=True)

    def compute_entry_hash(self, entry: AuditLog) -> str:
        """
        Compute the hash for an audit log entry.
        
        The hash is computed over:
        1. All entry fields (excluding entry_hash itself)
        2. The previous_hash (creating the chain)
        """
        data = self._create_entry_data(entry)
        return self._compute_hash(data)

    def get_last_hash(self, db: Session) -> Optional[str]:
        """
        Get the hash of the most recent audit log entry.
        
        Returns None if no entries exist (for the first entry).
        """
        last_entry = db.query(AuditLog)\
            .order_by(desc(AuditLog.id))\
            .first()
        
        if last_entry is None:
            return None
        
        return last_entry.entry_hash

    def create_entry_with_integrity(
        self,
        db: Session,
        agent_id: int,
        resource: str,
        action: str,
        decision: bool,
        reason: Optional[str] = None,
    ) -> AuditLog:
        """
        Create a new audit log entry with integrity hash.
        
        This method:
        1. Gets the hash of the previous entry
        2. Creates the new entry with previous_hash
        3. Computes the entry_hash
        4. Saves to database
        """
        # Get the hash of the previous entry
        previous_hash = self.get_last_hash(db)
        
        # Create the new entry
        entry = AuditLog(
            agent_id=agent_id,
            resource=resource,
            action=action,
            decision=decision,
            reason=reason,
            previous_hash=previous_hash,
            entry_hash="",  # Will be computed below
        )
        
        # Compute the hash for this entry
        entry.entry_hash = self.compute_entry_hash(entry)
        
        # Save to database
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return entry

    def verify_entry(self, entry: AuditLog) -> bool:
        """
        Verify the integrity of a single audit log entry.
        
        Returns True if the entry's hash is valid.
        """
        expected_hash = self.compute_entry_hash(entry)
        return entry.entry_hash == expected_hash

    def verify_chain(self, db: Session, limit: int = 1000) -> Dict[str, Any]:
        """
        Verify the integrity of the audit log chain.
        
        Checks:
        1. Each entry's hash matches its computed hash
        2. Each entry's previous_hash matches the previous entry's hash
        3. The chain is continuous (no gaps)
        
        Returns a dictionary with verification results.
        """
        entries = db.query(AuditLog)\
            .order_by(AuditLog.id)\
            .limit(limit)\
            .all()
        
        if not entries:
            return {
                "valid": True,
                "entries_checked": 0,
                "errors": [],
                "message": "No entries to verify"
            }
        
        errors = []
        previous_hash = None
        
        for i, entry in enumerate(entries):
            # Check if entry hash is valid
            if not self.verify_entry(entry):
                errors.append({
                    "entry_id": entry.id,
                    "error": "Invalid entry hash",
                    "expected": self.compute_entry_hash(entry),
                    "actual": entry.entry_hash,
                })
            
            # Check if previous_hash matches
            if entry.previous_hash != previous_hash:
                errors.append({
                    "entry_id": entry.id,
                    "error": "Previous hash mismatch",
                    "expected": previous_hash,
                    "actual": entry.previous_hash,
                })
            
            previous_hash = entry.entry_hash
        
        return {
            "valid": len(errors) == 0,
            "entries_checked": len(entries),
            "errors": errors,
            "message": "Chain integrity verified" if len(errors) == 0 else f"Found {len(errors)} integrity errors"
        }

    def get_chain_info(self, db: Session) -> Dict[str, Any]:
        """
        Get information about the audit log chain.
        
        Returns chain statistics and current state.
        """
        total_entries = db.query(AuditLog).count()
        
        if total_entries == 0:
            return {
                "total_entries": 0,
                "chain_length": 0,
                "first_entry_id": None,
                "last_entry_id": None,
                "last_hash": None,
            }
        
        first_entry = db.query(AuditLog).order_by(AuditLog.id).first()
        last_entry = db.query(AuditLog).order_by(desc(AuditLog.id)).first()
        
        return {
            "total_entries": total_entries,
            "chain_length": total_entries,
            "first_entry_id": first_entry.id,
            "last_entry_id": last_entry.id,
            "last_hash": last_entry.entry_hash,
        }


# Singleton instance
audit_integrity_service = AuditIntegrityService()
