import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from sse_starlette.sse import EventSourceResponse

from .core.config import settings
from .core.security import get_current_user, create_access_token
from .core.middleware import PIIRedactionMiddleware, AuditLogMiddleware, RequestLoggingMiddleware
from .api.v1.endpoints import agentic, documents, traces, qa, compare, audit, settings, memory, summarizer, translator, sentiment, agents
from .services.agent_service import AgentService
from .services.memory_service import MemoryService
from .core.monitoring import setup_monitoring, instrument_fastapi

# Global agent service instance
agent_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent_service
    
    # Startup
    print("🚀 Starting Smart Document Bot...")
    
    # Initialize agent service
    agent_service = AgentService()
    print("✅ Agent service initialized")
    
    # Setup monitoring
    setup_monitoring()
    print("✅ Monitoring setup complete")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Smart Document Bot...")
    if agent_service:
        await agent_service.cleanup_old_processing_history()
    print("✅ Cleanup complete")

# Create FastAPI app
app = FastAPI(
    title="Smart Document Bot API",
    description="AI-powered document processing and analysis system",
    version="1.0.0",
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

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PIIRedactionMiddleware)
app.add_middleware(AuditLogMiddleware)

# Dependency to get agent service
def get_agent_service() -> AgentService:
    """Get the global agent service instance"""
    if agent_service is None:
        raise RuntimeError("Agent service not initialized")
    return agent_service

# Override dependency injection for endpoints
app.dependency_overrides[AgentService] = get_agent_service

# Include routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    agentic.router,
    prefix="/api/v1/agentic",
    tags=["Agentic Processing"]
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    traces.router,
    prefix="/api/v1/traces",
    tags=["Agent Traces"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    qa.router,
    prefix="/api/v1/qa",
    tags=["Question Answering"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    compare.router,
    prefix="/api/v1/compare",
    tags=["Document Comparison"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    audit.router,
    prefix="/api/v1/audit",
    tags=["Audit Trail"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    settings.router,
    prefix="/api/v1/settings",
    tags=["Settings"]
)

app.include_router(
    memory.router,
    prefix="/api/v1/memory",
    tags=["Memory"]
)

app.include_router(
    summarizer.router,
    prefix="/api/v1/summarizer",
    tags=["Document Summarization"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    translator.router,
    prefix="/api/v1/translator",
    tags=["Document Translation"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    sentiment.router,
    prefix="/api/v1/sentiment",
    tags=["Sentiment Analysis"],
    dependencies=[Depends(get_agent_service)]
)

app.include_router(
    agents.router,
    prefix="/api/v1/agents",
    tags=["Agent Management"],
    dependencies=[Depends(get_agent_service)]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Document Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Agent capabilities endpoint
@app.get("/api/v1/agents/capabilities")
async def get_agent_capabilities(agent_service: AgentService = Depends(get_agent_service)):
    """Get information about available agents and their capabilities"""
    return agent_service.get_agent_capabilities()

# System status endpoint
@app.get("/api/v1/system/status")
async def get_system_status(agent_service: AgentService = Depends(get_agent_service)):
    """Get system status and health information"""
    return {
        "status": "operational",
        "agents": agent_service.get_agent_capabilities(),
        "workflow_status": agent_service.get_workflow_status(),
        "processing_history": len(agent_service.get_all_processing_history())
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
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
