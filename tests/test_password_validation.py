import pytest
from app.core.security import validate_password, PasswordValidationError


class TestPasswordValidation:
    """Test password complexity requirements."""

    def test_valid_password(self):
        """Password meeting all requirements should pass."""
        validate_password("SecureP@ss123")  # Should not raise

    def test_minimum_length(self):
        """Password shorter than 12 chars should fail."""
        with pytest.raises(PasswordValidationError, match="at least 12 characters"):
            validate_password("Short1!")

    def test_uppercase_required(self):
        """Password without uppercase should fail."""
        with pytest.raises(PasswordValidationError, match="uppercase"):
            validate_password("alllowercase1!")

    def test_lowercase_required(self):
        """Password without lowercase should fail."""
        with pytest.raises(PasswordValidationError, match="lowercase"):
            validate_password("ALLUPPERCASE1!")

    def test_digit_required(self):
        """Password without digit should fail."""
        with pytest.raises(PasswordValidationError, match="digit"):
            validate_password("NoDigitsHere!")

    def test_special_char_required(self):
        """Password without special char should fail."""
        with pytest.raises(PasswordValidationError, match="special"):
            validate_password("NoSpecial1234")

    def test_multiple_failures(self):
        """Password failing multiple checks should list all."""
        with pytest.raises(PasswordValidationError):
            validate_password("short")

    def test_exactly_12_chars_valid(self):
        """Password with exactly 12 chars meeting all criteria should pass."""
        validate_password("Abcdefgh1!xy")  # Should not raise

    def test_common_special_chars(self):
        """Various special characters should be accepted."""
        for char in "!@#$%^&*()_+-=":
            pw = f"ValidPass12{char}x"
            validate_password(pw)  # Should not raise
