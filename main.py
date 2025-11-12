"""
Main Application Entry Point
=============================

This is the main FastAPI application that brings together all routes,
middleware, and configuration.

The application provides:
- RESTful API endpoints for all features
- JWT authentication and authorization
- CORS configuration for frontend access
- WebSocket support for real-time updates
- Error handling and logging
- Health checks and monitoring

Run the application:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from typing import AsyncGenerator

from app.config import settings
from app.database import init_db, check_db_connection
from app.utils.encryption import validate_encryption_key

# Import routers (will be created)
from app.routers import (
    auth,
    users,
    companies,
    devices,
    invitations,
    google_drive,
    health
)

# ============================================================
# Logging Configuration
# ============================================================
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# Application Lifespan Events
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager for startup and shutdown events.

    Startup:
    - Validate encryption key
    - Check database connection
    - Initialize database tables
    - Log application info

    Shutdown:
    - Close connections
    - Cleanup resources
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")

    try:
        # Validate encryption key
        if not validate_encryption_key():
            raise ValueError("Invalid encryption key configuration")
        logger.info("Encryption key validated")

        # Check database connection
        if not check_db_connection():
            raise ConnectionError("Cannot connect to database")
        logger.info("Database connection established")

        # Initialize database (create tables if they don't exist)
        # In production, use Alembic migrations instead
        if settings.APP_ENV == "development":
            init_db()
            logger.info("Database initialized")

        logger.info(f"Application started successfully on {settings.HOST}:{settings.PORT}")

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down...")


# ============================================================
# FastAPI Application Instance
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Simple Digital Signage platform with multi-tenant support",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,  # Disable in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)


# ============================================================
# CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Custom Middleware
# ============================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add X-Process-Time header to all responses.
    Useful for monitoring API performance.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests.
    """
    logger.info(f"{request.method} {request.url.path} - {request.client.host}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
    return response


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed error messages.
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.
    """
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.APP_ENV == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "docs": "/api/docs" if settings.DEBUG else "disabled",
        "status": "running"
    }


# ============================================================
# Router Registration
# ============================================================

# API v1 routes
API_V1_PREFIX = "/api/v1"

app.include_router(
    health.router,
    prefix=API_V1_PREFIX,
    tags=["Health"]
)

app.include_router(
    auth.router,
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["Authentication"]
)

app.include_router(
    companies.router,
    prefix=f"{API_V1_PREFIX}/companies",
    tags=["Companies"]
)

app.include_router(
    users.router,
    prefix=f"{API_V1_PREFIX}/users",
    tags=["Users"]
)

app.include_router(
    devices.router,
    prefix=f"{API_V1_PREFIX}/devices",
    tags=["Devices"]
)

app.include_router(
    invitations.router,
    prefix=f"{API_V1_PREFIX}/invitations",
    tags=["Invitations"]
)

app.include_router(
    google_drive.router,
    prefix=f"{API_V1_PREFIX}/google-drive",
    tags=["Google Drive"]
)


# ============================================================
# Development Server
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
