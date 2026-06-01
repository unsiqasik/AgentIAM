"""
Tests for the rate limiter functionality.
"""

import time
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.rate_limiter import InMemoryRateLimiter, get_client_ip, check_rate_limit


class TestInMemoryRateLimiter:
    """Test the InMemoryRateLimiter class."""

    def setup_method(self):
        """Set up a fresh rate limiter for each test."""
        self.limiter = InMemoryRateLimiter()

    def test_allows_requests_under_limit(self):
        """Requests under the limit should be allowed."""
        # Mock settings
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 5
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            for i in range(5):
                is_allowed, headers = self.limiter.is_allowed("192.168.1.1")
                assert is_allowed is True
                assert int(headers["X-RateLimit-Remaining"]) == 4 - i
        finally:
            rl_module.settings = original_settings

    def test_blocks_requests_over_limit(self):
        """Requests exceeding the limit should be blocked."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 3
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            # Fill up the limit
            for _ in range(3):
                self.limiter.is_allowed("192.168.1.1")

            # Next request should be blocked
            is_allowed, headers = self.limiter.is_allowed("192.168.1.1")
            assert is_allowed is False
            assert headers["X-RateLimit-Remaining"] == "0"
        finally:
            rl_module.settings = original_settings

    def test_different_ips_independent(self):
        """Rate limits should be tracked independently per IP."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 2
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            # Fill up IP1
            self.limiter.is_allowed("192.168.1.1")
            self.limiter.is_allowed("192.168.1.1")

            # IP2 should still be allowed
            is_allowed, _ = self.limiter.is_allowed("192.168.1.2")
            assert is_allowed is True

            # IP1 should be blocked
            is_allowed, _ = self.limiter.is_allowed("192.168.1.1")
            assert is_allowed is False
        finally:
            rl_module.settings = original_settings

    def test_window_expiration(self):
        """Requests should be allowed after the window expires."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 2
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 1  # 1 second window
        rl_module.settings = mock_settings

        try:
            # Fill up the limit
            self.limiter.is_allowed("192.168.1.1")
            self.limiter.is_allowed("192.168.1.1")

            # Should be blocked
            is_allowed, _ = self.limiter.is_allowed("192.168.1.1")
            assert is_allowed is False

            # Wait for window to expire
            time.sleep(1.1)

            # Should be allowed again
            is_allowed, _ = self.limiter.is_allowed("192.168.1.1")
            assert is_allowed is True
        finally:
            rl_module.settings = original_settings

    def test_response_headers(self):
        """Response headers should contain rate limit info."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 10
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            _, headers = self.limiter.is_allowed("192.168.1.1")
            assert "X-RateLimit-Limit" in headers
            assert "X-RateLimit-Remaining" in headers
            assert "X-RateLimit-Reset" in headers
            assert headers["X-RateLimit-Limit"] == "10"
            assert headers["X-RateLimit-Remaining"] == "9"
        finally:
            rl_module.settings = original_settings


class TestGetClientIp:
    """Test the get_client_ip function."""

    def test_direct_connection(self):
        """Should return direct client IP."""
        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.1"
        assert get_client_ip(request) == "192.168.1.1"

    def test_forwarded_for(self):
        """Should return first IP from X-Forwarded-For."""
        request = MagicMock()
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        assert get_client_ip(request) == "10.0.0.1"

    def test_real_ip(self):
        """Should return X-Real-IP header value."""
        request = MagicMock()
        request.headers = {"X-Real-IP": "10.0.0.2"}
        assert get_client_ip(request) == "10.0.0.2"

    def test_no_client(self):
        """Should return 'unknown' when client is None."""
        request = MagicMock()
        request.headers = {}
        request.client = None
        assert get_client_ip(request) == "unknown"


class TestCheckRateLimit:
    """Test the check_rate_limit dependency."""

    def test_allows_requests_under_limit(self):
        """Should allow requests under the rate limit."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 100
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            app = FastAPI()

            @app.get("/test", dependencies=[Depends(check_rate_limit)])
            async def test_endpoint():
                return {"message": "ok"}

            client = TestClient(app)
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"message": "ok"}
        finally:
            rl_module.settings = original_settings

    def test_blocks_requests_over_limit(self):
        """Should return 429 when rate limit is exceeded."""
        import app.core.rate_limiter as rl_module
        original_settings = rl_module.settings

        mock_settings = MagicMock()
        mock_settings.RATE_LIMIT_REQUESTS = 2
        mock_settings.RATE_LIMIT_WINDOW_SECONDS = 60
        rl_module.settings = mock_settings

        try:
            # Reset the global limiter
            original_limiter = rl_module.rate_limiter
            rl_module.rate_limiter = InMemoryRateLimiter()

            app = FastAPI()

            @app.get("/test", dependencies=[Depends(check_rate_limit)])
            async def test_endpoint():
                return {"message": "ok"}

            client = TestClient(app)

            # First two requests should succeed
            assert client.get("/test").status_code == 200
            assert client.get("/test").status_code == 200

            # Third request should be rate limited
            response = client.get("/test")
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]["error"]
        finally:
            rl_module.settings = original_settings
            rl_module.rate_limiter = original_limiter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
