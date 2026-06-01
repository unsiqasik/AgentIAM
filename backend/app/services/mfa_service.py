"""
Multi-Factor Authentication (MFA) service using TOTP.

Provides:
- TOTP secret generation
- QR code generation for authenticator apps
- TOTP code verification
- MFA enable/disable functionality
"""

import base64
import io
from typing import Optional

import pyotp
import qrcode
from sqlalchemy.orm import Session

from app.models.user import User


class MFAService:
    """Service for handling Multi-Factor Authentication operations."""

    def __init__(self):
        self.issuer_name = "AgentIAM"

    def generate_secret(self) -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()

    def get_totp_uri(self, secret: str, username: str) -> str:
        """Generate TOTP URI for QR code generation."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=self.issuer_name)

    def generate_qr_code(self, secret: str, username: str) -> str:
        """
        Generate QR code as base64-encoded PNG image.

        Returns:
            Base64-encoded PNG image string
        """
        uri = self.get_totp_uri(secret, username)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    def verify_totp(self, secret: str, code: str) -> bool:
        """
        Verify a TOTP code against the secret.

        Args:
            secret: The TOTP secret
            code: The 6-digit TOTP code to verify

        Returns:
            True if the code is valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    def enable_mfa(self, db: Session, user: User, secret: str, code: str) -> bool:
        """
        Enable MFA for a user after verifying the TOTP code.

        Args:
            db: Database session
            user: User to enable MFA for
            secret: The TOTP secret
            code: The 6-digit TOTP code to verify

        Returns:
            True if MFA was enabled successfully, False if verification failed
        """
        if not self.verify_totp(secret, code):
            return False

        user.mfa_enabled = True
        user.mfa_secret = secret
        db.commit()
        return True

    def disable_mfa(self, db: Session, user: User, code: str) -> bool:
        """
        Disable MFA for a user after verifying the TOTP code.

        Args:
            db: Database session
            user: User to disable MFA for
            code: The 6-digit TOTP code to verify

        Returns:
            True if MFA was disabled successfully, False if verification failed
        """
        if not user.mfa_enabled or not user.mfa_secret:
            return False

        if not self.verify_totp(user.mfa_secret, code):
            return False

        user.mfa_enabled = False
        user.mfa_secret = None
        db.commit()
        return True


# Singleton instance
mfa_service = MFAService()
