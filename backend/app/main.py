import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from sse_starlette.sse import EventSourceResponse

from .core.config import settings
from .core.security import get_current_user, create_access_token
from .core.middleware import PIIRedactionMiddleware, AuditLogMiddleware
from .api.v1.endpoints import agentic, documents, traces, qa, compare, audit, auth, settings, memory
from .services.agent_service import AgentService
from .services.memory_service import MemoryService
from .core.monitoring import setup_monitoring, instrument_fastapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting REDLINE Regulatory Document Intelligence Platform...")
    
    # Initialize services
    app.state.agent_service = AgentService()
    app.state.memory_service = MemoryService()
    
    # Setup monitoring
    setup_monitoring()
    instrument_fastapi(app)
    
    print("✅ Services initialized successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down REDLINE...")


# Create FastAPI app
app = FastAPI(
    title="REDLINE - Regulatory Document Intelligence Platform",
    description="Agentic system for regulatory document processing and compliance analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PIIRedactionMiddleware)
app.add_middleware(AuditLogMiddleware)

# Dependency injection
def get_agent_service() -> AgentService:
    return app.state.agent_service

def get_memory_service() -> MemoryService:
    return app.state.memory_service

# Override dependency injection for endpoints
app.dependency_overrides[AgentService] = get_agent_service
app.dependency_overrides[MemoryService] = get_memory_service

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agentic.router, prefix="/api/v1/agentic", tags=["Agentic Processing"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["Agent Traces"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["Q&A"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Document Comparison"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "REDLINE - Regulatory Document Intelligence Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "agent_service": "operational",
            "memory_service": "operational"
        }
    }


@app.get("/api/v1/stream/agent-trace/{trace_id}")
async def stream_agent_trace(
    trace_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stream live agent trace updates"""
    
    async def event_generator():
        """Generate SSE events for agent trace updates"""
        try:
            while True:
                # Get latest trace updates
                trace_updates = await app.state.agent_service.get_trace_updates(trace_id)
                
                if trace_updates:
                    yield {
                        "event": "trace_update",
                        "data": trace_updates
                    }
                
                # Check if trace is complete
                if await app.state.agent_service.is_trace_complete(trace_id):
                    yield {
                        "event": "trace_complete",
                        "data": {"trace_id": trace_id}
                    }
                    break
                
                await asyncio.sleep(1)  # Poll every second
                
        except Exception as e:
            yield {
                "event": "error",
                "data": {"error": str(e)}
            }
    
    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
