"""
Audit Log Integrity API endpoints.

Provides:
- Chain verification
- Chain information
- Individual entry verification
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.audit_integrity_service import audit_integrity_service

router = APIRouter()


class ChainVerificationResponse(BaseModel):
    """Response for chain verification."""
    valid: bool
    entries_checked: int
    errors: list
    message: str


class ChainInfoResponse(BaseModel):
    """Response for chain information."""
    total_entries: int
    chain_length: int
    first_entry_id: int = None
    last_entry_id: int = None
    last_hash: str = None


class EntryVerificationResponse(BaseModel):
    """Response for entry verification."""
    entry_id: int
    valid: bool
    message: str


@router.get("/verify", response_model=ChainVerificationResponse)
def verify_chain(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = 1000,
) -> Any:
    """
    Verify the integrity of the audit log chain.
    
    Checks:
    1. Each entry's hash matches its computed hash
    2. Each entry's previous_hash matches the previous entry's hash
    3. The chain is continuous (no gaps)
    
    Parameters:
    - limit: Maximum number of entries to verify (default: 1000)
    """
    result = audit_integrity_service.verify_chain(db, limit=limit)
    return ChainVerificationResponse(**result)


@router.get("/info", response_model=ChainInfoResponse)
def get_chain_info(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get information about the audit log chain.
    
    Returns chain statistics and current state.
    """
    info = audit_integrity_service.get_chain_info(db)
    return ChainInfoResponse(**info)


@router.get("/verify/{entry_id}", response_model=EntryVerificationResponse)
def verify_entry(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    entry_id: int,
) -> Any:
    """
    Verify the integrity of a single audit log entry.
    
    Parameters:
    - entry_id: ID of the entry to verify
    """
    entry = db.query(AuditLog).filter(AuditLog.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    is_valid = audit_integrity_service.verify_entry(entry)
    
    return EntryVerificationResponse(
        entry_id=entry_id,
        valid=is_valid,
        message="Entry integrity verified" if is_valid else "Entry hash mismatch - possible tampering detected"
    )
