import os
from typing import Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response

from .config import settings

# Initialize OpenTelemetry
trace.set_tracer_provider(TracerProvider())
metrics.set_meter_provider(MeterProvider())

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_AGENTS = Gauge(
    'active_agents',
    'Number of active agents'
)

DOCUMENT_PROCESSING_TIME = Histogram(
    'document_processing_duration_seconds',
    'Document processing duration',
    ['document_type', 'agent_type']
)

AGENT_CONFIDENCE = Histogram(
    'agent_confidence_scores',
    'Agent confidence scores',
    ['agent_type']
)

# Custom metrics
documents_processed = meter.create_counter(
    name="documents_processed",
    description="Number of documents processed"
)

agent_executions = meter.create_counter(
    name="agent_executions",
    description="Number of agent executions",
    attributes={"agent_type": ""}
)

processing_time = meter.create_histogram(
    name="processing_time",
    description="Processing time in seconds",
    attributes={"operation": ""}
)


def setup_monitoring():
    """Setup OpenTelemetry and Prometheus monitoring"""
    if not settings.ENABLE_TRACING:
        return
    
    # Add span processor
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    
    # Add metric reader
    metrics.get_meter_provider().add_metric_reader(
        PeriodicExportingMetricReader(ConsoleMetricExporter())
    )
    
    print("📊 Monitoring setup complete")


def instrument_fastapi(app):
    """Instrument FastAPI with OpenTelemetry"""
    if settings.ENABLE_TRACING:
        FastAPIInstrumentor.instrument_app(app)


def instrument_redis():
    """Instrument Redis with OpenTelemetry"""
    if settings.ENABLE_TRACING:
        RedisInstrumentor().instrument()


def instrument_postgres():
    """Instrument PostgreSQL with OpenTelemetry"""
    if settings.ENABLE_TRACING:
        Psycopg2Instrumentor().instrument()


def record_request_metrics(request: Request, response: Response, duration: float):
    """Record request metrics"""
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)


def record_agent_execution(agent_type: str, confidence: float, duration: float):
    """Record agent execution metrics"""
    agent_executions.add(1, {"agent_type": agent_type})
    AGENT_CONFIDENCE.labels(agent_type=agent_type).observe(confidence)
    processing_time.record(duration, {"operation": f"agent_{agent_type}"})


def record_document_processing(doc_type: str, agent_type: str, duration: float):
    """Record document processing metrics"""
    documents_processed.add(1)
    DOCUMENT_PROCESSING_TIME.labels(
        document_type=doc_type,
        agent_type=agent_type
    ).observe(duration)


def set_active_agents(count: int):
    """Set active agents count"""
    ACTIVE_AGENTS.set(count)


def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()


def get_metrics_content_type():
    """Get Prometheus metrics content type"""
    return CONTENT_TYPE_LATEST
