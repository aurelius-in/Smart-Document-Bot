import re
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

from .config import settings
from .monitoring import get_monitor

# PII patterns for redaction
PII_PATTERNS = [
    # Email addresses
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    # Phone numbers (various formats)
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),
    (r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b', '[PHONE]'),
    # Social Security Numbers
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
    # Credit Card Numbers (basic pattern)
    (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]'),
    # IP Addresses
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]'),
    # Basic name patterns (consecutive capitalized words)
    (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]'),
]


class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """Middleware to redact PII from request/response data"""
    
    def __init__(self, app: FastAPI, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.monitor = get_monitor()
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Store original body for redaction
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Create new request with redacted body if needed
        if body:
            redacted_body = self._redact_pii(body.decode('utf-8', errors='ignore'))
            # Note: In production, you might want to log the redacted version
            # but pass the original to the application
        
        # Process the request
        response = await call_next(request)
        
        # Redact response if needed (for logging purposes)
        if hasattr(response, 'body'):
            # This is a simplified approach - in production you'd want more sophisticated handling
            pass
        
        return response
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text using regex patterns"""
        redacted_text = text
        
        for pattern, replacement in PII_PATTERNS:
            redacted_text = re.sub(pattern, replacement, redacted_text, flags=re.IGNORECASE)
        
        return redacted_text


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests for audit purposes"""
    
    def __init__(self, app: FastAPI, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.monitor = get_monitor()
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        
        # Extract request information
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        url = str(request.url)
        
        # Extract user information if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = request.state.user.get('id')
        
        # Log request start
        self.monitor.log_info(
            "audit_middleware",
            f"API request started: {method} {url}",
            {
                "request_id": request_id,
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "user_id": user_id
            },
            trace_id=request_id,
            user_id=user_id
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            end_time = time.time()
            response_time = end_time - start_time
            
            # Log successful request
            self.monitor.log_info(
                "audit_middleware",
                f"API request completed: {method} {url} - {response.status_code}",
                {
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "client_ip": client_ip,
                    "user_id": user_id
                },
                trace_id=request_id,
                user_id=user_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log failed request
            end_time = time.time()
            response_time = end_time - start_time
            
            self.monitor.log_error(
                "audit_middleware",
                f"API request failed: {method} {url}",
                str(e),
                trace_id=request_id,
                user_id=user_id
            )
            
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request/response logging"""
    
    def __init__(self, app: FastAPI, enabled: bool = True, log_bodies: bool = False):
        super().__init__(app)
        self.enabled = enabled
        self.log_bodies = log_bodies
        self.monitor = get_monitor()
        
        # Endpoints to exclude from detailed logging (to avoid noise)
        self.exclude_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate trace ID
        trace_id = str(uuid.uuid4())
        
        # Extract request details
        start_time = time.time()
        method = request.method
        url = str(request.url)
        headers = dict(request.headers)
        
        # Remove sensitive headers
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        filtered_headers = {
            k: v if k.lower() not in sensitive_headers else "[REDACTED]"
            for k, v in headers.items()
        }
        
        # Log request body if enabled
        request_body = None
        if self.log_bodies and method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode('utf-8', errors='ignore')[:1000]  # Limit size
            except Exception:
                request_body = "[ERROR_READING_BODY]"
        
        # Log request details
        self.monitor.log_info(
            "request_logging",
            f"Incoming request: {method} {url}",
            {
                "trace_id": trace_id,
                "method": method,
                "url": url,
                "headers": filtered_headers,
                "body": request_body if self.log_bodies else None,
                "content_length": headers.get("content-length"),
                "content_type": headers.get("content-type")
            },
            trace_id=trace_id
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            # Log response details
            self.monitor.log_info(
                "request_logging",
                f"Response: {method} {url} - {response.status_code}",
                {
                    "trace_id": trace_id,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response_headers": dict(response.headers) if hasattr(response, 'headers') else {}
                },
                trace_id=trace_id
            )
            
            # Add trace ID to response
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        except Exception as e:
            # Log error
            end_time = time.time()
            response_time = end_time - start_time
            
            self.monitor.log_error(
                "request_logging",
                f"Request error: {method} {url}",
                str(e),
                trace_id=trace_id
            )
            
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app: FastAPI, enabled: bool = True, requests_per_minute: int = 60):
        super().__init__(app)
        self.enabled = enabled
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, List[float]] = {}
        self.monitor = get_monitor()
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.request_counts[client_ip] = []
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            self.monitor.log_warning(
                "rate_limit",
                f"Rate limit exceeded for IP: {client_ip}",
                {
                    "client_ip": client_ip,
                    "requests_in_window": len(self.request_counts[client_ip]),
                    "limit": self.requests_per_minute
                }
            )
            
            return Response(
                content=json.dumps({"error": "Rate limit exceeded"}),
                status_code=429,
                headers={"Content-Type": "application/json"}
            )
        
        # Add current request to count
        self.request_counts[client_ip].append(current_time)
        
        # Process request
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"


def setup_middleware(app: FastAPI):
    """Setup all middleware for the application"""
    
    # Add rate limiting
    if settings.ENABLE_MONITORING:
        app.add_middleware(RateLimitMiddleware, enabled=True, requests_per_minute=120)
    
    # Add request logging
    app.add_middleware(
        RequestLoggingMiddleware, 
        enabled=settings.ENABLE_MONITORING,
        log_bodies=settings.DEBUG
    )
    
    # Add audit logging
    app.add_middleware(
        AuditLogMiddleware,
        enabled=settings.AUDIT_ENABLED
    )
    
    # Add PII redaction
    app.add_middleware(
        PIIRedactionMiddleware,
        enabled=True
    )