"""
Health Check Router
===================

Provides endpoints for monitoring application health and status.
These endpoints are typically used by:
- Load balancers
- Monitoring systems
- DevOps teams

Endpoints:
- GET /health - Basic health check
- GET /health/detailed - Detailed system status
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict
import logging

from app.database import get_db, check_db_connection
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str]
)
async def health_check():
    """
    Basic health check endpoint.

    Returns a simple OK response if the application is running.
    Use this for load balancer health checks.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get(
    "/health/detailed",
    status_code=status.HTTP_200_OK,
    response_model=Dict
)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with system information.

    Checks:
    - Application status
    - Database connectivity
    - Configuration status

    Returns:
        dict: Detailed system status

    Example Response:
        {
            "status": "healthy",
            "service": "Simple Digital Signage",
            "version": "1.0.0",
            "environment": "development",
            "database": "connected",
            "components": {
                "api": "operational",
                "database": "operational",
                "encryption": "operational"
            }
        }
    """
    # Check database connection
    db_status = "connected" if check_db_connection() else "disconnected"

    # Build health response
    health_status = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
        "components": {
            "api": "operational",
            "database": "operational" if db_status == "connected" else "unavailable",
            "encryption": "operational"
        },
        "features": {
            "rate_limiting": settings.ENABLE_RATE_LIMITING,
            "monitoring": settings.ENABLE_MONITORING,
            "analytics": settings.ENABLE_ANALYTICS
        }
    }

    return health_status


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK
)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if the application is ready to serve traffic.
    Returns 503 if the application is not ready.

    Returns:
        dict: Readiness status
    """
    if not check_db_connection():
        logger.error("Readiness check failed: database unavailable")
        return {
            "status": "not_ready",
            "reason": "database_unavailable"
        }

    return {
        "status": "ready"
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK
)
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if the application process is alive.
    A failure here would indicate the container should be restarted.

    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive"
    }
