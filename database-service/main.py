import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from datetime import datetime

from app.core.config import settings
from app.core.database import connect_to_mongo, disconnect_from_mongo
from app.routers.users import router as users_router
from app.core.security import api_auth_dependency

# Configure logging based on settings
log_format = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if settings.LOG_FORMAT == 'TEXT'
    else '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE_PATH) if settings.LOG_FILE_ENABLED else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="HackIt Database Service",
    description="""
    ## Centralized Database API Service for HackIt Organization
    
    This service provides unified database operations through RESTful APIs, 
    eliminating direct MongoDB model dependencies across multiple projects.
    
    ### Features
    - 🔐 **HMAC-SHA256 Authentication** - Military-grade security
    - 🚀 **Complete CRUD Operations** - Full user management
    - 🔍 **Advanced Search & Filtering** - Powerful query capabilities
    - 📊 **Analytics & Statistics** - User insights and metrics
    - 🏷️ **Tag Management** - Flexible user categorization
    - 📱 **Mobile-Friendly** - Responsive API design
    
    ### Security
    - Request signing with timestamp validation
    - Rate limiting and domain whitelisting
    - Comprehensive audit logging
    """,
    version=settings.SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "User Management",
            "description": "Operations for managing user accounts, profiles, and authentication."
        },
        {
            "name": "System",
            "description": "System health checks and service information."
        }
    ]
)

# Add security middleware
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for consistent error responses."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if settings.is_production():
        # Don't expose internal errors in production
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    else:
        # Show detailed errors in development
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(exc),
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.utcnow().isoformat(),
                "detail": str(exc)
            }
        )

# Include routers with authentication dependency
app.include_router(
    users_router,
    dependencies=[Depends(api_auth_dependency)] if settings.is_production() else []
)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Rate limiting: {'enabled' if settings.API_RATE_LIMIT_ENABLED else 'disabled'}")
    
    # Connect to database
    try:
        connect_to_mongo()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    
    logger.info(f"{settings.SERVICE_NAME} started successfully on {settings.SERVICE_HOST}:{settings.SERVICE_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on service shutdown."""
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    
    try:
        disconnect_from_mongo()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during database disconnection: {str(e)}")
    
    logger.info(f"{settings.SERVICE_NAME} shut down successfully")

# System endpoints
@app.get("/health", tags=["System"], summary="Health Check", description="Check service health and status")
async def health_check():
    """Health check endpoint with detailed service information."""
    from app.services.user_service import UserService
    
    try:
        # Test database connectivity
        user_count = UserService.get_user_count()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
        user_count = 0
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": db_status,
            "user_count": user_count
        },
        "features": {
            "rate_limiting": settings.API_RATE_LIMIT_ENABLED,
            "audit_logging": settings.FEATURES_AUDIT_LOGGING,
            "schema_validation": settings.FEATURES_SCHEMA_VALIDATION
        }
    }

@app.get("/", tags=["System"], summary="Service Information", description="Get service information and available endpoints")
async def root():
    """Root endpoint with comprehensive service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "description": "Centralized database API service for HackIt organization",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "users": {
                "base": "/users",
                "create": "POST /users/",
                "get_by_id": "GET /users/{user_id}",
                "get_by_email": "GET /users/email/{email}",
                "get_by_discord": "GET /users/discord/{user_id}/{guild_id}",
                "update": "PUT /users/{user_id}",
                "delete": "DELETE /users/{user_id}",
                "query": "POST /users/query",
                "list": "GET /users/",
                "search": "GET /users/search/name/{name}",
                "tags": "GET /users/tag/{tag}",
                "statistics": "GET /users/analytics/statistics"
            }
        },
        "authentication": {
            "method": "HMAC-SHA256",
            "headers": ["X-API-Timestamp", "X-API-Signature"],
            "validity_window": f"{settings.SIGNATURE_VALIDITY_WINDOW} seconds"
        },
        "rate_limiting": {
            "enabled": settings.API_RATE_LIMIT_ENABLED,
            "requests_per_minute": settings.API_RATE_LIMIT_REQUESTS if settings.API_RATE_LIMIT_ENABLED else None
        }
    }

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Get OpenAPI specification."""
    from fastapi.openapi.utils import get_openapi
    
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Development helper endpoints (only in development mode)
if settings.is_development():
    from app.core.security import create_test_signature
    
    @app.get("/dev/test-signature", tags=["Development"], summary="Generate Test Signature")
    async def generate_test_signature(
        method: str = "GET",
        path: str = "/users/"
    ):
        """Generate test API signature for development (development mode only)."""
        return {
            "method": method.upper(),
            "path": path,
            "headers": create_test_signature(method, path),
            "note": "This endpoint is only available in development mode"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.is_development(),
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    ) 