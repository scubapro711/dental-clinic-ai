"""
DentalAI Backend - FastAPI Application

This is the main entry point for the DentalAI SaaS platform backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="DentalAI API",
    description="AI-powered SaaS platform for dental clinics",
    version="14.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - Allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
from app.api.v1 import api_router

app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to DentalAI API",
        "version": "14.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "dentalai-backend",
            "version": "14.0.0",
        },
    )


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": {
            "authentication": "active",
            "agents": "pending",
            "odoo_integration": "pending",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
