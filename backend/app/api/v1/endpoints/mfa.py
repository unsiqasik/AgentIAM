"""
Multi-Factor Authentication (MFA) API endpoints.

Provides:
- MFA setup (generate QR code)
- MFA enable (verify and enable)
- MFA disable (verify and disable)
- MFA status check
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.services.mfa_service import mfa_service

router = APIRouter()


class MFASetupResponse(BaseModel):
    """Response for MFA setup endpoint."""
    secret: str
    qr_code: str  # Base64-encoded PNG image
    uri: str  # TOTP URI for manual entry


class MFAVerifyRequest(BaseModel):
    """Request for MFA verification."""
    code: str  # 6-digit TOTP code


class MFAStatusResponse(BaseModel):
    """Response for MFA status endpoint."""
    enabled: bool
    has_secret: bool


@router.post("/setup", response_model=MFASetupResponse)
def setup_mfa(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Set up MFA for the current user.

    Generates a new TOTP secret and QR code for authenticator app setup.
    The secret is NOT saved until MFA is explicitly enabled via the /enable endpoint.
    """
    # Generate new secret
    secret = mfa_service.generate_secret()
    uri = mfa_service.get_totp_uri(secret, current_user.username)
    qr_code = mfa_service.generate_qr_code(secret, current_user.username)

    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        uri=uri,
    )


@router.post("/enable")
def enable_mfa(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    mfa_data: MFAVerifyRequest,
) -> Any:
    """
    Enable MFA for the current user.

    Requires:
    - secret: The TOTP secret from /setup endpoint
    - code: A valid 6-digit TOTP code from the authenticator app

    The request body should include:
    - code: 6-digit TOTP code
    - secret: TOTP secret (from setup)

    Returns success status.
    """
    # For enable, we need the secret from the setup step
    # In a real implementation, you'd store this temporarily or require it in the request
    # For simplicity, we'll accept it in the request body
    raise HTTPException(
        status_code=501,
        detail="MFA enable endpoint requires secret in request body. Use /enable-with-secret instead."
    )


@router.post("/enable-with-secret")
def enable_mfa_with_secret(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    mfa_data: dict,
) -> Any:
    """
    Enable MFA for the current user with secret.

    Request body:
    - secret: TOTP secret from /setup endpoint
    - code: 6-digit TOTP code from authenticator app

    Returns success status.
    """
    secret = mfa_data.get("secret")
    code = mfa_data.get("code")

    if not secret or not code:
        raise HTTPException(
            status_code=400,
            detail="Both 'secret' and 'code' are required."
        )

    if mfa_service.enable_mfa(db, current_user, secret, code):
        return {"message": "MFA enabled successfully", "enabled": True}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid TOTP code. Please try again."
        )


@router.post("/disable")
def disable_mfa(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    mfa_data: MFAVerifyRequest,
) -> Any:
    """
    Disable MFA for the current user.

    Requires a valid 6-digit TOTP code to disable MFA.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=400,
            detail="MFA is not enabled for this user."
        )

    if mfa_service.disable_mfa(db, current_user, mfa_data.code):
        return {"message": "MFA disabled successfully", "enabled": False}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid TOTP code. Please try again."
        )


@router.get("/status", response_model=MFAStatusResponse)
def get_mfa_status(
    *,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get MFA status for the current user.
    """
    return MFAStatusResponse(
        enabled=current_user.mfa_enabled,
        has_secret=current_user.mfa_secret is not None,
    )
