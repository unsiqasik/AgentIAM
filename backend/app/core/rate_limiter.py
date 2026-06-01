"""
In-memory rate limiter for FastAPI endpoints.

Uses a sliding window approach to track request counts per client IP.
Configurable via environment variables:
- RATE_LIMIT_REQUESTS: Max requests per window (default: 100)
- RATE_LIMIT_WINDOW_SECONDS: Window duration in seconds (default: 60)
"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException
from app.core.config import settings


class InMemoryRateLimiter:
    """Sliding window rate limiter using in-memory storage."""

    def __init__(self):
        # Store: {client_ip: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)

    def _cleanup_old_entries(self, client_ip: str, window_seconds: int):
        """Remove entries older than the window."""
        cutoff = time.time() - window_seconds
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

    def is_allowed(self, client_ip: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if a request from client_ip is allowed.

        Returns:
            Tuple of (is_allowed, rate_limit_headers)
        """
        max_requests = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        window_seconds = getattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 60)

        self._cleanup_old_entries(client_ip, window_seconds)

        current_count = len(self._requests[client_ip])
        remaining = max(0, max_requests - current_count)

        headers = {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time() + window_seconds)),
        }

        if current_count >= max_requests:
            return False, headers

        self._requests[client_ip].append(time.time())
        headers["X-RateLimit-Remaining"] = str(max(0, remaining - 1))

        return True, headers


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxy headers."""
    # Check for forwarded headers (common in production behind proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain (original client)
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"


async def check_rate_limit(request: Request):
    """
    FastAPI dependency for rate limiting.

    Usage:
        @router.post("/endpoint", dependencies=[Depends(check_rate_limit)])
        async def endpoint():
            ...
    """
    client_ip = get_client_ip(request)
    is_allowed, headers = rate_limiter.is_allowed(client_ip)

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {headers['X-RateLimit-Limit']} per window.",
                "retry_after": headers["X-RateLimit-Reset"],
            },
            headers=headers,
        )

    # Store headers in request state for response middleware
    request.state.rate_limit_headers = headers
    return True
