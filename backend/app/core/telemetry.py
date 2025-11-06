"""
OpenTelemetry configuration for DentaFlow backend.

This module sets up distributed tracing using OpenTelemetry with Google Cloud Trace.
"""

import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

logger = logging.getLogger(__name__)


def setup_opentelemetry(app_env: str = "production", service_version: str = "1.0.0"):
    """
    Initialize OpenTelemetry instrumentation for the application.
    
    This function:
    1. Creates a resource with service metadata
    2. Sets up OTLP exporter for Google Cloud Trace
    3. Configures the tracer provider
    4. Instruments common libraries (FastAPI, SQLAlchemy, requests, httpx)
    
    Args:
        app_env: Application environment (production, staging, development)
        service_version: Version of the service
    
    Environment Variables:
        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint (default: https://telemetry.googleapis.com)
        GCP_PROJECT_ID: Google Cloud project ID
        OTEL_TRACES_SAMPLER: Sampling strategy (default: always_on)
        OTEL_TRACES_SAMPLER_ARG: Sampling ratio for traceidratio sampler
    """
    try:
        # Get configuration from environment
        project_id = os.getenv("GCP_PROJECT_ID", "dentaflow-production")
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://telemetry.googleapis.com")
        
        # Determine service name based on environment
        service_name = f"dentaflow-backend-{app_env}" if app_env != "production" else "dentaflow-backend"
        
        # Create resource with service metadata
        resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "gcp.project_id": project_id,
            "deployment.environment": app_env,
        })
        
        logger.info(f"Initializing OpenTelemetry for {service_name} (version {service_version})")
        logger.info(f"OTLP endpoint: {otlp_endpoint}")
        logger.info(f"GCP Project: {project_id}")
        
        # Create tracer provider with resource
        tracer_provider = TracerProvider(resource=resource)
        
        # Set up OTLP exporter
        # Authentication is handled automatically via Application Default Credentials (ADC)
        # in Cloud Run environment
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            # Headers are added automatically by google-auth library
        )
        
        # Add batch span processor for efficient export
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Set the global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        logger.info("✅ OpenTelemetry tracer provider initialized successfully")
        
        return tracer_provider
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenTelemetry: {e}")
        logger.warning("Application will continue without tracing")
        return None


def instrument_app(app):
    """
    Instrument FastAPI application and common libraries.
    
    This function should be called after the FastAPI app is created.
    It adds automatic instrumentation for:
    - FastAPI endpoints (HTTP requests/responses)
    - SQLAlchemy (database queries)
    - requests library (HTTP client calls)
    - httpx library (async HTTP client calls)
    
    Args:
        app: FastAPI application instance
    """
    try:
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ FastAPI instrumented")
        
        # Instrument SQLAlchemy (will auto-detect engines)
        SQLAlchemyInstrumentor().instrument()
        logger.info("✅ SQLAlchemy instrumented")
        
        # Instrument requests library
        RequestsInstrumentor().instrument()
        logger.info("✅ requests library instrumented")
        
        # Instrument httpx library
        HTTPXClientInstrumentor().instrument()
        logger.info("✅ httpx library instrumented")
        
        logger.info("🎉 All instrumentations completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to instrument libraries: {e}")
        logger.warning("Some traces may not be collected")


def get_tracer(name: str = __name__):
    """
    Get a tracer instance for creating custom spans.
    
    Usage:
        from app.core.telemetry import get_tracer
        
        tracer = get_tracer(__name__)
        
        with tracer.start_as_current_span("my_operation"):
            # Your code here
            pass
    
    Args:
        name: Name of the tracer (usually __name__ of the module)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
