"""
================================================================================
AI DENTAL CLINIC MANAGEMENT SYSTEM - GATEWAY SERVICE
================================================================================

Copyright (c) 2025 Eran Sarfaty. All Rights Reserved.
🔒 PROPRIETARY SOFTWARE - PATENT PENDING INNOVATIONS 🔒

Gateway Service - Main Entry Point
שכבת השער הראשית של מערכת ניהול המרפאה

PROTECTED INTELLECTUAL PROPERTY:
This module contains patentable AI orchestration algorithms.
Unauthorized copying or commercial use is strictly prohibited.

For licensing: scubapro711@gmail.com | +972-53-555-0317
================================================================================
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from datetime import datetime
from typing import Dict, Any

from .webhooks_router import router as webhooks_router
from . import api
from .middleware import setup_middleware
from .config import get_settings
from .services.message_service import message_service
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="מערכת ניהול מרפאת שיניים - Gateway",
    description="שכבת השער לניהול תקשורת עם מטופלים באמצעות בינה מלאכותית",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(webhooks_router, prefix="/webhook", tags=["webhooks"])
app.include_router(api.router, prefix="/api", tags=["api"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await message_service.initialize()
        logger.info("Gateway services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing gateway services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    try:
        await message_service.cleanup()
        logger.info("Gateway services cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up gateway services: {e}")

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "Dental Clinic AI Gateway",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "description": "מערכת ניהול מרפאת שיניים עם בינה מלאכותית"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # TODO: Add actual health checks (database, redis, etc.)
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "gateway": "up",
                "database": "up",  # TODO: implement actual check
                "redis": "up",     # TODO: implement actual check
                "ai_agents": "up"  # TODO: implement actual check
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "אירעה שגיאה במערכת. אנא נסה שוב מאוחר יותר.",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower()
    )
