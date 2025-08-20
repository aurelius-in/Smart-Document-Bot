import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.middleware import setup_middleware
from .core.monitoring import setup_monitoring, instrument_fastapi
from .database.connection import init_database, check_database_connection
from .services.agent_service import AgentService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
agent_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent_service
    
    # Startup
    logger.info("Starting AI Document Agent application...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_database()
        
        # Check database connection
        logger.info("Checking database connection...")
        await check_database_connection()
        
        # Initialize agent service
        logger.info("Initializing agent service...")
        agent_service = AgentService()
        await agent_service.initialize()
        
        # Setup monitoring
        if settings.ENABLE_MONITORING:
            logger.info("Setting up monitoring...")
            setup_monitoring()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Document Agent application...")
    
    try:
        if agent_service:
            await agent_service.cleanup()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Application shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-Grade AI Document Processing & Analysis Platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Setup monitoring
if settings.ENABLE_MONITORING:
    instrument_fastapi(app)


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    try:
        # Check database connection
        await check_database_connection()
        
        # Check agent service
        if agent_service:
            service_status = await agent_service.get_status()
        else:
            service_status = "not_initialized"
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": settings.APP_VERSION,
            "database": "connected",
            "agent_service": service_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": settings.APP_VERSION,
            "components": {}
        }
        
        # Database health
        try:
            await check_database_connection()
            health_status["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        # Agent service health
        if agent_service:
            try:
                service_status = await agent_service.get_status()
                health_status["components"]["agent_service"] = {
                    "status": "healthy",
                    "message": "Agent service operational",
                    "details": service_status
                }
            except Exception as e:
                health_status["components"]["agent_service"] = {
                    "status": "unhealthy",
                    "message": f"Agent service failed: {str(e)}"
                }
                health_status["status"] = "degraded"
        else:
            health_status["components"]["agent_service"] = {
                "status": "not_initialized",
                "message": "Agent service not initialized"
            }
        
        # Redis health
        try:
            import redis
            redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            redis_client.ping()
            health_status["components"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection successful"
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}"
            }
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Enterprise-Grade AI Document Processing & Analysis Platform",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        },
        "features": [
            "Multi-Agent AI Processing",
            "Document Intelligence",
            "Enterprise Security",
            "Real-time Analytics",
            "Compliance Monitoring"
        ]
    }


# API status endpoint
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": {
            "auth": "/api/v1/auth",
            "documents": "/api/v1/documents",
            "agents": "/api/v1/agents",
            "analytics": "/api/v1/analytics"
        }
    }


# Include API routers
from .api.v1.endpoints import (
    auth, agentic, documents, traces, qa, compare, 
    audit, settings, memory, summarizer, translator, 
    sentiment, agents
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(agentic.router, prefix="/api/v1/agentic", tags=["Agentic Processing"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["Agent Traces"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["Question Answering"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Document Comparison"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit Trail"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory Management"])
app.include_router(summarizer.router, prefix="/api/v1/summarizer", tags=["Document Summarization"])
app.include_router(translator.router, prefix="/api/v1/translator", tags=["Document Translation"])
app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment Analysis"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agent Management"])


# Agent capabilities endpoint
@app.get("/api/v1/agents/capabilities")
async def get_agent_capabilities():
    """Get all available agent capabilities"""
    return {
        "agents": {
            "orchestrator": {
                "description": "Workflow orchestration and coordination",
                "capabilities": ["workflow_planning", "execution_monitoring", "resource_allocation"]
            },
            "ingestion": {
                "description": "Document ingestion and content extraction",
                "capabilities": ["text_extraction", "metadata_extraction", "format_detection"]
            },
            "classifier": {
                "description": "Document classification and categorization",
                "capabilities": ["document_classification", "domain_detection", "content_categorization"]
            },
            "entity": {
                "description": "Named entity recognition and extraction",
                "capabilities": ["entity_extraction", "relationship_mapping", "entity_linking"]
            },
            "risk": {
                "description": "Risk assessment and compliance monitoring",
                "capabilities": ["risk_assessment", "compliance_checking", "policy_enforcement"]
            },
            "qa": {
                "description": "Question answering and document querying",
                "capabilities": ["question_answering", "context_retrieval", "answer_generation"]
            },
            "compare": {
                "description": "Document comparison and diff analysis",
                "capabilities": ["document_comparison", "change_detection", "similarity_analysis"]
            },
            "audit": {
                "description": "Audit logging and compliance tracking",
                "capabilities": ["audit_logging", "compliance_tracking", "event_monitoring"]
            },
            "summarizer": {
                "description": "Document summarization and key point extraction",
                "capabilities": ["extractive_summarization", "abstractive_summarization", "key_point_extraction"]
            },
            "translator": {
                "description": "Multi-language document translation",
                "capabilities": ["language_detection", "document_translation", "quality_assessment"]
            },
            "sentiment": {
                "description": "Sentiment analysis and tone detection",
                "capabilities": ["sentiment_analysis", "tone_detection", "emotion_recognition"]
            }
        },
        "total_agents": 11,
        "total_capabilities": 33
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
