"""
DentalAI Backend - FastAPI Application

This is the main entry point for the DentalAI SaaS platform backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# OpenAPI metadata
tags_metadata = [
    {
        "name": "AI Chat",
        "description": """
        Multi-agent AI chat system with streaming support.
        
        **Agents:**
        - **Alex** - Patient interactions and appointment management
        - **Marcus** - Financial analysis and revenue optimization
        - **Sarah** - Clinical decision support and treatment planning
        - **Sophia** - Practice administration and operations
        
        **Features:**
        - Real-time streaming via Server-Sent Events (SSE)
        - Conversation memory and context
        - Tool execution (Odoo, database, external APIs)
        - Suggested actions generation
        - Multi-turn conversations
        """,
    },
    {
        "name": "Decision Queue",
        "description": """
        Proactive suggestions and decision management.
        
        AI agents continuously monitor the clinic and generate proactive suggestions
        for staff to review and approve. This enables an agentic, proactive workflow
        where AI takes initiative rather than waiting for user queries.
        
        **Features:**
        - Proactive suggestions from all agents
        - Priority-based queue (urgent, high, medium, low)
        - Approval/rejection workflow
        - Learning feedback collection
        - Execution tracking
        - Statistics and analytics
        """,
    },
    {
        "name": "Fine-Tuning",
        "description": """
        AI agent fine-tuning and continuous learning.
        
        Collect feedback on agent responses and use it to fine-tune the underlying
        language models. This enables continuous improvement and adaptation to
        clinic-specific workflows and terminology.
        
        **Features:**
        - Feedback collection (1-5 star ratings)
        - Training data management
        - OpenAI fine-tuning job creation
        - Training readiness checking
        - Model performance tracking
        """,
    },
    {
        "name": "Authentication",
        "description": """
        User authentication and authorization.
        
        **Supported Methods:**
        - Email/password with JWT tokens
        - Google OAuth 2.0
        - AWS Cognito
        
        **Roles:**
        - **super_admin** - Full system access
        - **org_admin** - Organization administration
        - **org_staff** - Staff member access
        - **org_viewer** - Read-only access (patients)
        """,
    },
    {
        "name": "Patients",
        "description": "Patient management and medical records",
    },
    {
        "name": "Appointments",
        "description": "Appointment scheduling and management",
    },
    {
        "name": "Financial",
        "description": "Financial analytics and revenue tracking",
    },
    {
        "name": "Dashboard",
        "description": "Dashboard metrics and statistics",
    },
    {
        "name": "Organizations",
        "description": "Organization and clinic management",
    },
]

# Create FastAPI app
app = FastAPI(
    title="DentaFlow API",
    description="""
    # DentaFlow - AI-Powered Dental Practice Management
    
    DentaFlow is a comprehensive SaaS platform for dental clinics featuring:
    
    ## 🤖 Multi-Agent AI System
    
    Four specialized AI agents work together to manage your practice:
    
    - **Alex** 👨‍⚕️ - Patient Experience Agent
      - Appointment scheduling and reminders
      - Patient communication
      - Intake and follow-up
    
    - **Marcus** 💰 - Financial Intelligence Agent
      - Revenue analysis and forecasting
      - Collections management
      - Financial insights
    
    - **Sarah** 🩺 - Clinical Decision Support Agent
      - Treatment planning assistance
      - Clinical documentation
      - Evidence-based recommendations
    
    - **Sophia** 📊 - Practice Operations Agent
      - Staff scheduling
      - Inventory management
      - Operational efficiency
    
    ## 🚀 Key Features
    
    - **Agentic/Proactive AI** - Agents take initiative and suggest actions
    - **Decision Queue** - Review and approve AI suggestions
    - **Streaming Chat** - Real-time conversations with AI agents
    - **Fine-Tuning** - Continuous learning from feedback
    - **Odoo Integration** - Full ERP integration for patient data
    - **Multi-Portal** - Separate clinic and patient portals
    - **RBAC** - Role-based access control
    - **Real-time Updates** - WebSocket support
    
    ## 🔐 Authentication
    
    All endpoints require authentication via JWT token in the `Authorization` header:
    
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    
    ## 📚 API Versioning
    
    Current version: **v1**  
    Base path: `/api/v1`
    
    ## 🌐 Environments
    
    - **Production:** https://api.dentaflow.ai
    - **Staging:** https://staging-api.dentaflow.ai
    - **Development:** http://localhost:8002
    
    ## 📞 Support
    
    - Email: support@dentaflow.ai
    - Documentation: https://docs.dentaflow.ai
    - Status: https://status.dentaflow.ai
    """,
    version="24.0.3",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "DentaFlow Support",
        "email": "support@dentaflow.ai",
        "url": "https://dentaflow.ai/support",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://dentaflow.ai/terms",
    },
    servers=[
        {
            "url": "https://api.dentaflow.ai",
            "description": "Production server",
        },
        {
            "url": "https://staging-api.dentaflow.ai",
            "description": "Staging server",
        },
        {
            "url": "http://localhost:8002",
            "description": "Development server",
        },
    ],
)

# Rate limiting middleware
from app.middleware.rate_limiter import (
    limiter,
    rate_limit_exceeded_handler,
    SlowAPIMiddleware
)
from slowapi.errors import RateLimitExceeded

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
from app.api.v1 import api_router

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message.
    
    Returns basic information about the API and links to documentation.
    """
    return {
        "message": "Welcome to DentaFlow API",
        "version": "20.3.0",
        "status": "running",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and Docker healthcheck.
    
    Returns the service health status and version information.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "dentaflow-backend",
            "version": "24.0.3",
            "phase": "Phase 4 - Production Ready",
        },
    )


@app.get("/api/v1/status", tags=["Status"])
async def api_status():
    """
    API status endpoint with feature availability.
    
    Returns the current operational status of all API features.
    """
    return {
        "api_version": "v1",
        "status": "operational",
        "features": {
            "authentication": "active",
            "ai_agents": "active",
            "decision_queue": "active",
            "fine_tuning": "active",
            "odoo_integration": "active",
            "streaming_chat": "active",
            "patient_portal": "active",
            "rbac": "active",
        },
        "agents": {
            "alex": "active",
            "marcus": "active",
            "sarah": "active",
            "sophia": "active",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

