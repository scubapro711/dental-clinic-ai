"""
Performance Monitoring Middleware

Tracks and logs application performance metrics:
- Request/response times
- Database query times
- Slow endpoint detection
- Memory usage
- Error rates
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import psutil
import logging
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)

# Performance metrics storage
class PerformanceMetrics:
    """In-memory performance metrics storage"""
    
    def __init__(self):
        self.request_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.slow_requests: List[Dict] = []
        
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record request metrics"""
        self.request_times[endpoint].append(duration)
        self.request_counts[endpoint] += 1
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
        
        # Track slow requests
        if duration > 0.5:  # > 500ms
            self.slow_requests.append({
                "endpoint": endpoint,
                "duration": duration,
                "status_code": status_code,
                "timestamp": datetime.utcnow()
            })
            
            # Keep only last 100 slow requests
            if len(self.slow_requests) > 100:
                self.slow_requests = self.slow_requests[-100:]
    
    def get_stats(self, endpoint: str = None) -> Dict:
        """Get performance statistics"""
        if endpoint:
            times = self.request_times.get(endpoint, [])
            if not times:
                return {}
            
            return {
                "endpoint": endpoint,
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "p50": self._percentile(times, 50),
                "p95": self._percentile(times, 95),
                "p99": self._percentile(times, 99),
                "errors": self.error_counts.get(endpoint, 0),
                "error_rate": self.error_counts.get(endpoint, 0) / len(times) * 100
            }
        
        # Overall stats
        all_times = []
        for times in self.request_times.values():
            all_times.extend(times)
        
        if not all_times:
            return {}
        
        return {
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "avg_response_time": sum(all_times) / len(all_times),
            "p50": self._percentile(all_times, 50),
            "p95": self._percentile(all_times, 95),
            "p99": self._percentile(all_times, 99),
            "slow_requests": len(self.slow_requests),
            "endpoints": len(self.request_times)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global metrics instance
metrics = PerformanceMetrics()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking application performance.
    
    Features:
    - Request/response time tracking
    - Slow endpoint detection
    - Error rate monitoring
    - Memory usage tracking
    - Performance headers
    """
    
    SLOW_REQUEST_THRESHOLD = 0.5  # 500ms
    
    async def dispatch(self, request: Request, call_next):
        # Skip health check and metrics endpoints
        if request.url.path in ["/health", "/metrics", "/api/v1/health"]:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"after {duration:.3f}s - {str(e)}"
            )
            
            # Record error metrics
            endpoint = self._get_endpoint_key(request)
            metrics.record_request(endpoint, duration, 500)
            
            raise
        
        # Calculate metrics
        duration = time.time() - start_time
        memory_used = self._get_memory_usage() - start_memory
        
        # Record metrics
        endpoint = self._get_endpoint_key(request)
        metrics.record_request(endpoint, duration, response.status_code)
        
        # Log slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.3f}s (status: {response.status_code})"
            )
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        response.headers["X-Memory-Used"] = f"{memory_used:.2f}"
        
        return response
    
    def _get_endpoint_key(self, request: Request) -> str:
        """Get normalized endpoint key"""
        # Remove IDs from path for grouping
        # /api/v1/patients/123 -> /api/v1/patients/{id}
        path = request.url.path
        parts = path.split("/")
        
        normalized = []
        for part in parts:
            if part.isdigit():
                normalized.append("{id}")
            else:
                normalized.append(part)
        
        return f"{request.method} {'/'.join(normalized)}"
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024


# Database query performance tracking
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time"""
    conn.info.setdefault('query_start_time', []).append(time.time())
    conn.info.setdefault('query_count', 0)
    conn.info['query_count'] += 1


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query completion and log slow queries"""
    total = time.time() - conn.info['query_start_time'].pop()
    
    # Log slow queries (> 100ms)
    if total > 0.1:
        # Truncate long queries
        query = statement[:500] + "..." if len(statement) > 500 else statement
        logger.warning(
            f"Slow query ({total:.3f}s): {query}"
        )


# API endpoint for performance metrics
from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/performance")
async def get_performance_metrics(endpoint: str = None):
    """
    Get performance metrics.
    
    Args:
        endpoint: Optional endpoint to get specific metrics for
    
    Returns:
        Performance statistics
    """
    if endpoint:
        return metrics.get_stats(endpoint)
    
    return metrics.get_stats()


@router.get("/slow-requests")
async def get_slow_requests(limit: int = 20):
    """
    Get recent slow requests.
    
    Args:
        limit: Maximum number of slow requests to return
    
    Returns:
        List of slow requests
    """
    return metrics.slow_requests[-limit:]


@router.get("/system")
async def get_system_metrics():
    """
    Get system resource metrics.
    
    Returns:
        CPU, memory, and disk usage
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "available": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total / 1024 / 1024 / 1024,  # GB
            "used": psutil.disk_usage('/').used / 1024 / 1024 / 1024,  # GB
            "percent": psutil.disk_usage('/').percent
        }
    }


@router.post("/reset")
async def reset_metrics():
    """Reset performance metrics"""
    global metrics
    metrics = PerformanceMetrics()
    return {"message": "Metrics reset successfully"}
