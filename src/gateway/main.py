"""
Gateway Service - Main Entry Point
שכבת השער הראשית של מערכת ניהול המרפאה
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from datetime import datetime
from typing import Dict, Any

from .webhooks import whatsapp_webhook, telegram_webhook
from .api import appointments_router, patients_router
from .api.ai_router import router as ai_router
from .api.queue_router import router as queue_router
from .middleware import setup_middleware
from .config import get_settings
from .services.message_service import message_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="מערכת ניהול מרפאת שיניים - Gateway",
    description="שכבת השער לניהול תקשורת עם מטופלים באמצעות בינה מלאכותית",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(whatsapp_webhook.router, prefix="/webhook", tags=["webhooks"])
app.include_router(telegram_webhook.router, prefix="/webhook", tags=["webhooks"])
app.include_router(appointments_router.router, prefix="/api", tags=["appointments"])
app.include_router(patients_router.router, prefix="/api", tags=["patients"])
app.include_router(ai_router, prefix="/api", tags=["ai"])
app.include_router(queue_router, prefix="/api", tags=["queue"])

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
