import time
import logging
import json
from typing import Callable, Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all incoming requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} - "
                f"Exception: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add CSP header if not already present
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:;"
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.redis_client:
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        try:
            key = f"rate_limit:{client_ip}"
            current_requests = self.redis_client.get(key)
            
            if current_requests is None:
                self.redis_client.setex(key, settings.RATE_LIMIT_WINDOW, 1)
            else:
                current_requests = int(current_requests)
                if current_requests >= settings.RATE_LIMIT_REQUESTS:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Limit: {settings.RATE_LIMIT_REQUESTS} per {settings.RATE_LIMIT_WINDOW} seconds"
                        }
                    )
                
                self.redis_client.incr(key)
                
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Continue without rate limiting if Redis fails
        
        return await call_next(request)


class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """Middleware for redacting PII from logs"""
    
    def __init__(self, app):
        super().__init__(app)
        self.pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
            r'\b\d{10,11}\b',  # Phone numbers
        ]
    
    def redact_pii(self, text: str) -> str:
        """Redact PII from text"""
        import re
        for pattern in self.pii_patterns:
            text = re.sub(pattern, '[REDACTED]', text)
        return text
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Redact PII from request body if present
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode()
                    redacted_body = self.redact_pii(body_str)
                    # Create new request with redacted body
                    request._body = redacted_body.encode()
            except Exception as e:
                logger.error(f"PII redaction failed: {e}")
        
        return await call_next(request)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip audit logging for health checks and static files
        if request.url.path in ["/health", "/health/detailed", "/docs", "/redoc"]:
            return await call_next(request)
        
        # Get user info if authenticated
        user_id = None
        user_email = None
        try:
            # This would be set by authentication middleware
            user_id = getattr(request.state, "user_id", None)
            user_email = getattr(request.state, "user_email", None)
        except Exception:
            pass
        
        # Log audit event
        audit_event = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
            "user_id": user_id,
            "user_email": user_email,
        }
        
        logger.info(f"AUDIT: {json.dumps(audit_event)}")
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and logging errors"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # Log the error
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}: {str(e)}",
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "path": request.url.path
                }
            )


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting metrics"""
    
    def __init__(self, app, metrics_collector=None):
        super().__init__(app)
        self.metrics_collector = metrics_collector
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        
        # Record metrics if collector is available
        if self.metrics_collector:
            try:
                self.metrics_collector.record_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration=process_time
                )
            except Exception as e:
                logger.error(f"Failed to record metrics: {e}")
        
        return response


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure based on your deployment
    )
    
    # Add custom middleware in order
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(PIIRedactionMiddleware)
    app.add_middleware(AuditLogMiddleware)
    
    # Add rate limiting middleware if Redis is available
    try:
        import redis
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()  # Test connection
        app.add_middleware(RateLimitMiddleware, redis_client=redis_client)
        logger.info("Rate limiting middleware enabled")
    except Exception as e:
        logger.warning(f"Rate limiting middleware disabled: {e}")
    
    # Add metrics middleware if monitoring is enabled
    if settings.ENABLE_MONITORING:
        try:
            from .monitoring import MetricsCollector
            metrics_collector = MetricsCollector()
            app.add_middleware(MetricsMiddleware, metrics_collector=metrics_collector)
            logger.info("Metrics middleware enabled")
        except Exception as e:
            logger.warning(f"Metrics middleware disabled: {e}")
    
    logger.info("Middleware setup completed")


def get_request_info(request: Request) -> Dict[str, Any]:
    """Extract request information for logging"""
    return {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", ""),
    }


def get_response_info(response: Response) -> Dict[str, Any]:
    """Extract response information for logging"""
    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }