from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api import deps
from app.services.auth_service import auth_service
from app.services.mfa_service import mfa_service
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()


class LoginResponse(BaseModel):
    """Response for login endpoint."""
    access_token: str
    token_type: str
    mfa_required: bool = False
    mfa_temp_token: str = None


class MFAVerifyLoginRequest(BaseModel):
    """Request for MFA verification during login."""
    temp_token: str
    code: str


@router.post("/login/access-token", response_model=LoginResponse)
def login_access_token(
    *,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.

    If MFA is enabled for the user, returns mfa_required=True and a temp_token.
    The client must then call /login/verify-mfa with the temp_token and TOTP code.
    """
    user = auth_service.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Check if MFA is enabled
    if user.mfa_enabled:
        # Generate a temporary token for MFA verification
        # In a real implementation, you'd create a short-lived JWT
        import secrets
        temp_token = secrets.token_urlsafe(32)
        # Store temp_token -> user mapping (in production, use Redis or similar)
        # For now, we'll use a simple in-memory store
        if not hasattr(login_access_token, '_mfa_tokens'):
            login_access_token._mfa_tokens = {}
        login_access_token._mfa_tokens[temp_token] = user.id

        return LoginResponse(
            access_token="",
            token_type="bearer",
            mfa_required=True,
            mfa_temp_token=temp_token,
        )

    # No MFA required, return normal token
    token = auth_service.login(user)
    return LoginResponse(
        access_token=token.access_token,
        token_type=token.token_type,
    )


@router.post("/login/verify-mfa", response_model=Token)
def verify_mfa_login(
    *,
    db: Session = Depends(deps.get_db),
    mfa_data: MFAVerifyLoginRequest,
) -> Any:
    """
    Verify MFA code during login.

    Requires:
    - temp_token: Temporary token from /login/access-token
    - code: 6-digit TOTP code from authenticator app
    """
    # Get the temporary token store
    if not hasattr(login_access_token, '_mfa_tokens'):
        raise HTTPException(status_code=400, detail="No pending MFA verification")

    temp_token = mfa_data.temp_token
    if temp_token not in login_access_token._mfa_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired temp token")

    user_id = login_access_token._mfa_tokens[temp_token]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Verify the TOTP code
    if not mfa_service.verify_totp(user.mfa_secret, mfa_data.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    # Clean up temp token
    del login_access_token._mfa_tokens[temp_token]

    # Generate normal access token
    token = auth_service.login(user)
    return token
