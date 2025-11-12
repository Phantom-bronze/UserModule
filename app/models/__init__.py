"""
Database Models Package
=======================

This package contains all SQLAlchemy ORM models for the application.

Models represent database tables and define:
- Table structure (columns, data types, constraints)
- Relationships between tables (foreign keys, joins)
- Validation rules and constraints
- Model-level business logic

Available Models:
- User: User accounts with different roles (super_admin, admin, user)
- Company: Organizations/companies that users belong to
- Invitation: Invitation tokens for user registration
- GoogleCredential: Google Cloud credentials for companies
- Device: Smart TV devices linked to users
- GoogleDriveToken: Google Drive access tokens for users
- Content: Media content (images and videos)
- Playlist: Content playlists
- PlaylistContent: Junction table for playlist-content relationship
- AuditLog: Audit trail for all important actions

All models inherit from Base (defined in database.py) and use
SQLAlchemy ORM for database operations.
"""

# Import all models to make them available when importing from models package
from app.models.user import User
from app.models.company import Company
from app.models.invitation import Invitation
from app.models.google_credential import GoogleCredential
from app.models.device import Device
from app.models.google_drive_token import GoogleDriveToken
from app.models.audit_log import AuditLog

# Export all models for easy import
__all__ = [
    "User",
    "Company",
    "Invitation",
    "GoogleCredential",
    "Device",
    "GoogleDriveToken",
    "AuditLog",
]
