import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import connect_to_mongo, disconnect_from_mongo
from app.routers.users import router as users_router
from app.middleware.auth import api_auth_dependency

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HackIt Database Service",
    description="Centralized database API service for HackIt organization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with authentication dependency
app.include_router(
    users_router,
    dependencies=[Depends(api_auth_dependency)]
)

@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    logger.info("Starting Database Service...")
    connect_to_mongo()
    logger.info("Database Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from database on shutdown."""
    logger.info("Shutting down Database Service...")
    disconnect_from_mongo()
    logger.info("Database Service shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "database-service",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "HackIt Database Service",
        "version": "1.0.0",
        "description": "Centralized database API service",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "users": "/users"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True,
        log_level="info"
    ) 