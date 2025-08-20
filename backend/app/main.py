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
from .core.middleware import setup_middleware
from .database.connection import init_database, check_database_connection
from .api.v1.endpoints import auth, agentic, documents, traces, qa, compare, audit, settings, memory, summarizer, translator, sentiment, agents
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
    
    # Check database connection
    if check_database_connection():
        print("✅ Database connection verified")
        # Initialize database tables
        init_database()
        print("✅ Database initialized")
    else:
        print("⚠️ Database connection failed - using fallback mode")
    
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)

# Instrument FastAPI for monitoring
instrument_fastapi(app)

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
    return {
        "agents": [
            {
                "name": "OrchestratorAgent",
                "description": "Coordinates the overall document processing workflow",
                "capabilities": ["workflow_coordination", "task_scheduling", "error_handling"]
            },
            {
                "name": "IngestionAgent", 
                "description": "Handles document upload and initial processing",
                "capabilities": ["file_upload", "format_detection", "preprocessing"]
            },
            {
                "name": "ClassifierAgent",
                "description": "Categorizes documents by type and content",
                "capabilities": ["document_classification", "content_analysis", "metadata_extraction"]
            },
            {
                "name": "EntityAgent",
                "description": "Extracts key entities and information",
                "capabilities": ["entity_extraction", "named_entity_recognition", "relationship_mapping"]
            },
            {
                "name": "RiskAgent",
                "description": "Assesses compliance risks and issues",
                "capabilities": ["risk_assessment", "compliance_checking", "vulnerability_detection"]
            },
            {
                "name": "QAAgent",
                "description": "Provides intelligent Q&A capabilities",
                "capabilities": ["question_answering", "context_understanding", "knowledge_retrieval"]
            },
            {
                "name": "CompareAgent",
                "description": "Compares documents for similarities and differences",
                "capabilities": ["document_comparison", "similarity_analysis", "difference_detection"]
            },
            {
                "name": "AuditAgent",
                "description": "Monitors and logs all system activities",
                "capabilities": ["activity_logging", "audit_trail", "compliance_monitoring"]
            },
            {
                "name": "SummarizerAgent",
                "description": "Creates document summaries and insights",
                "capabilities": ["document_summarization", "key_point_extraction", "insight_generation"]
            },
            {
                "name": "TranslatorAgent",
                "description": "Handles multi-language document processing",
                "capabilities": ["language_translation", "multilingual_processing", "cultural_adaptation"]
            },
            {
                "name": "SentimentAnalysisAgent",
                "description": "Analyzes document sentiment and tone",
                "capabilities": ["sentiment_analysis", "tone_detection", "emotion_recognition"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
