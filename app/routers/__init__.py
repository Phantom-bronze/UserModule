"""
API Routers Package
===================

This package contains all API route handlers organized by feature:
- auth: Authentication and authorization
- users: User management
- companies: Company management
- devices: Device management
- invitations: User invitation system
- health: Health checks and system status
"""

from app.routers import (
    auth,
    users,
    companies,
    devices,
    invitations,
    health
)

__all__ = [
    "auth",
    "users",
    "companies",
    "devices",
    "invitations",
    "health"
]
