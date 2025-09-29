from fastapi import FastAPI
from .api import router as api_router
from .webhooks_router import router as webhooks_router
from .services.message_service import MessageService
from .config import get_settings
import logging

# Configure logging
from ..shared.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app(include_startup_events: bool = True) -> FastAPI:
    app = FastAPI(
        title=get_settings().title,
        description=get_settings().description,
        version=get_settings().version,
    )

    if include_startup_events:
        message_service: MessageService

        @app.on_event("startup")
        async def startup_event():
            """
            Initialize gateway services on startup.
            """
            nonlocal message_service
            try:
                message_service = MessageService()
                await message_service.initialize()
                logger.info("Message service initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing gateway services: {e}")

        @app.on_event("shutdown")
        async def shutdown_event():
            """
            Close gateway services on shutdown.
            """
            try:
                if 'message_service' in locals() and message_service:
                    await message_service.close()
                    logger.info("Message service closed successfully.")
            except Exception as e:
                logger.error(f"Error closing gateway services: {e}")

    @app.get("/health", summary="Health Check", description="Returns the health status of the gateway.")
    def health_check():
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")
    app.include_router(webhooks_router, prefix="/webhook")

    return app

app = create_app()



@app.get("/status", summary="System Status", description="Returns the status of various system components.")
async def get_status():
    # In a real application, this would check the status of the database, Redis, etc.
    return {
        "gateway": "ok",
        "database": "ok", # Placeholder
        "redis": "ok" # Placeholder
    }

