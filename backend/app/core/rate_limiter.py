"""
Rate Limiter for API Security
Prevents abuse and DOS attacks
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
            requests_per_day: Max requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # Storage: {identifier: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[float]] = defaultdict(list)
        
        # Last cleanup time
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self, identifier: str):
        """Remove requests older than 24 hours."""
        now = time.time()
        day_ago = now - 86400  # 24 hours
        
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > day_ago
        ]
        
        # Periodic full cleanup (every hour)
        if now - self.last_cleanup > 3600:
            self._full_cleanup()
            self.last_cleanup = now
    
    def _full_cleanup(self):
        """Remove all old requests from all identifiers."""
        now = time.time()
        day_ago = now - 86400
        
        # Clean up old requests
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > day_ago
            ]
            
            # Remove empty entries
            if not self.requests[identifier]:
                del self.requests[identifier]
        
        logger.info(f"Rate limiter cleanup: {len(self.requests)} active identifiers")
    
    def check_rate_limit(
        self,
        identifier: str,
        endpoint: Optional[str] = None
    ) -> None:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: User ID, IP address, or API key
            endpoint: Optional endpoint name for specific limits
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        now = time.time()
        
        # Cleanup old requests
        self._cleanup_old_requests(identifier)
        
        # Add current request
        self.requests[identifier].append(now)
        
        # Check limits
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400
        
        requests_last_minute = sum(1 for t in self.requests[identifier] if t > minute_ago)
        requests_last_hour = sum(1 for t in self.requests[identifier] if t > hour_ago)
        requests_last_day = sum(1 for t in self.requests[identifier] if t > day_ago)
        
        # Check minute limit
        if requests_last_minute > self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded (minute): {identifier} - "
                f"{requests_last_minute}/{self.requests_per_minute}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per minute",
                    "retry_after": 60
                }
            )
        
        # Check hour limit
        if requests_last_hour > self.requests_per_hour:
            logger.warning(
                f"Rate limit exceeded (hour): {identifier} - "
                f"{requests_last_hour}/{self.requests_per_hour}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per hour",
                    "retry_after": 3600
                }
            )
        
        # Check day limit
        if requests_last_day > self.requests_per_day:
            logger.warning(
                f"Rate limit exceeded (day): {identifier} - "
                f"{requests_last_day}/{self.requests_per_day}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": "requests per day",
                    "retry_after": 86400
                }
            )
        
        logger.debug(
            f"Rate limit OK: {identifier} - "
            f"{requests_last_minute}/min, {requests_last_hour}/hour, {requests_last_day}/day"
        )
    
    def get_stats(self, identifier: str) -> dict:
        """
        Get rate limit statistics for an identifier.
        
        Args:
            identifier: User ID, IP address, or API key
            
        Returns:
            Dictionary with statistics
        """
        now = time.time()
        self._cleanup_old_requests(identifier)
        
        minute_ago = now - 60
        hour_ago = now - 3600
        day_ago = now - 86400
        
        requests_last_minute = sum(1 for t in self.requests[identifier] if t > minute_ago)
        requests_last_hour = sum(1 for t in self.requests[identifier] if t > hour_ago)
        requests_last_day = sum(1 for t in self.requests[identifier] if t > day_ago)
        
        return {
            "identifier": identifier,
            "requests_last_minute": requests_last_minute,
            "requests_last_hour": requests_last_hour,
            "requests_last_day": requests_last_day,
            "limits": {
                "per_minute": self.requests_per_minute,
                "per_hour": self.requests_per_hour,
                "per_day": self.requests_per_day
            },
            "remaining": {
                "per_minute": max(0, self.requests_per_minute - requests_last_minute),
                "per_hour": max(0, self.requests_per_hour - requests_last_hour),
                "per_day": max(0, self.requests_per_day - requests_last_day)
            }
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
    
    return _rate_limiter


# Dependency for FastAPI
async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting.
    
    Usage:
        @app.post("/api/chat", dependencies=[Depends(rate_limit_dependency)])
        async def chat(message: str):
            ...
    """
    rate_limiter = get_rate_limiter()
    
    # Get identifier (user ID or IP address)
    identifier = None
    
    # Try to get user ID from request state (set by auth middleware)
    if hasattr(request.state, "user_id"):
        identifier = f"user:{request.state.user_id}"
    
    # Fallback to IP address
    if identifier is None:
        identifier = f"ip:{request.client.host}"
    
    # Check rate limit
    rate_limiter.check_rate_limit(identifier)


# Example usage
if __name__ == "__main__":
    # Test rate limiter
    limiter = RateLimiter(requests_per_minute=5, requests_per_hour=20, requests_per_day=100)
    
    # Simulate requests
    identifier = "test_user"
    
    print("Simulating 10 requests...")
    for i in range(10):
        try:
            limiter.check_rate_limit(identifier)
            print(f"Request {i+1}: ✅ OK")
            time.sleep(0.1)
        except HTTPException as e:
            print(f"Request {i+1}: ❌ Rate limit exceeded - {e.detail}")
    
    # Get stats
    stats = limiter.get_stats(identifier)
    print(f"\nStats: {stats}")
