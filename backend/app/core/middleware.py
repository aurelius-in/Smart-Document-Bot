import re
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from .config import settings


class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """Middleware for PII redaction in request/response bodies"""
    
    def __init__(self, app):
        super().__init__(app)
        self.pii_patterns = [
            (re.compile(pattern, re.IGNORECASE), "[REDACTED]")
            for pattern in settings.PII_PATTERNS
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and response for PII redaction"""
        
        # Redact PII in request body
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                redacted_body = self._redact_pii(body.decode())
                request._body = redacted_body.encode()
        
        # Process response
        response = await call_next(request)
        
        # Redact PII in response body
        if hasattr(response, 'body'):
            redacted_body = self._redact_pii(response.body.decode())
            response.body = redacted_body.encode()
        
        return response
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII patterns in text"""
        if not settings.ENABLE_PII_REDACTION:
            return text
        
        redacted_text = text
        for pattern, replacement in self.pii_patterns:
            redacted_text = pattern.sub(replacement, redacted_text)
        
        return redacted_text


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware for hash-chained audit logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.audit_logs = []
        self.previous_hash = None
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response for audit trail"""
        
        start_time = time.time()
        
        # Create audit entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "request_id": request.headers.get("x-request-id", self._generate_request_id()),
            "previous_hash": self.previous_hash,
            "request_size": len(await request.body()) if request.method in ["POST", "PUT", "PATCH"] else 0
        }
        
        # Process request
        response = await call_next(request)
        
        # Add response info
        audit_entry.update({
            "status_code": response.status_code,
            "response_size": len(response.body) if hasattr(response, 'body') else 0,
            "duration_ms": int((time.time() - start_time) * 1000)
        })
        
        # Calculate hash and add to chain
        entry_hash = self._calculate_hash(audit_entry)
        audit_entry["hash"] = entry_hash
        self.previous_hash = entry_hash
        
        # Store audit entry
        self.audit_logs.append(audit_entry)
        
        # Add audit headers to response
        response.headers["x-audit-hash"] = entry_hash
        response.headers["x-request-id"] = audit_entry["request_id"]
        
        return response
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return hashlib.sha256(f"{time.time()}{id(self)}".encode()).hexdigest()[:16]
    
    def _calculate_hash(self, entry: Dict[str, Any]) -> str:
        """Calculate hash for audit entry"""
        entry_str = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    def get_audit_logs(self) -> List[Dict[str, Any]]:
        """Get all audit logs"""
        return self.audit_logs.copy()
    
    def get_audit_chain(self) -> List[str]:
        """Get audit chain hashes"""
        return [entry["hash"] for entry in self.audit_logs]
