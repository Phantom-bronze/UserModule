"""
User Pydantic Schemas
=====================

This module defines Pydantic schemas for User-related API operations.

Schemas:
- UserCreate: For creating new users
- UserUpdate: For updating existing users
- UserResponse: For returning user data in responses
- UserListResponse: For returning lists of users

All schemas include validation rules and are used by FastAPI for:
- Request body validation
- Response serialization
- API documentation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.user import UserRole


# ============================================================
# User Create Schema
# ============================================================

class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    This schema is used when admins invite/create new users.
    The actual user record is created when the invitation is accepted.

    Fields:
        email: User's email address (required, must be valid email)
        full_name: User's full name (required)
        role: User role - admin or user (required)
        company_id: Company the user belongs to (required for non-super-admins)
        can_add_devices: Whether user can add new devices (optional, default False)

    Example Request Body:
        {
            "email": "newuser@example.com",
            "full_name": "John Doe",
            "role": "user",
            "company_id": "123e4567-e89b-12d3-a456-426614174000",
            "can_add_devices": true
        }
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="User's full name",
        example="John Doe"
    )

    role: UserRole = Field(
        default=UserRole.USER,
        description="User role (admin or user)",
        example="user"
    )

    company_id: Optional[uuid.UUID] = Field(
        None,
        description="Company ID (required for admins and users)",
        example="123e4567-e89b-12d3-a456-426614174000"
    )

    can_add_devices: bool = Field(
        default=False,
        description="Whether user can add new devices",
        example=True
    )

    @validator('role')
    def validate_role(cls, v):
        """
        Validate that role is not super_admin.

        Super admins cannot be created through the API - they are
        created manually or via initialization script.
        """
        if v == UserRole.SUPER_ADMIN:
            raise ValueError("Cannot create super admin users through API")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "user",
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "can_add_devices": True
            }
        }


# ============================================================
# User Update Schema
# ============================================================

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.

    All fields are optional - only provided fields will be updated.
    This allows for partial updates.

    Fields:
        full_name: User's full name (optional)
        profile_picture_url: Profile picture URL (optional)
        role: User role (optional)
        can_add_devices: Device permission (optional)
        is_active: Account status (optional)

    Example Request Body:
        {
            "full_name": "John Smith",
            "can_add_devices": true
        }
    """

    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="User's full name",
        example="John Smith"
    )

    profile_picture_url: Optional[str] = Field(
        None,
        description="Profile picture URL",
        example="https://example.com/photo.jpg"
    )

    role: Optional[UserRole] = Field(
        None,
        description="User role (admin or user)",
        example="admin"
    )

    can_add_devices: Optional[bool] = Field(
        None,
        description="Whether user can add new devices",
        example=True
    )

    is_active: Optional[bool] = Field(
        None,
        description="Account status",
        example=True
    )

    @validator('role')
    def validate_role(cls, v):
        """Validate that role is not super_admin."""
        if v == UserRole.SUPER_ADMIN:
            raise ValueError("Cannot change role to super_admin")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "full_name": "John Smith",
                "can_add_devices": True,
                "is_active": True
            }
        }


class UserPermissionsUpdate(BaseModel):
    """
    Schema for updating user permissions.

    This is used by admins to grant/revoke specific permissions
    for users in their company.

    Fields:
        can_add_devices: Whether user can add new devices

    Example Request Body:
        {
            "can_add_devices": true
        }
    """

    can_add_devices: bool = Field(
        ...,
        description="Whether user can add new devices",
        example=True
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "can_add_devices": True
            }
        }


# ============================================================
# User Response Schema
# ============================================================

class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    This schema represents a user object returned by the API.
    Sensitive data (passwords, tokens) are excluded.

    Fields:
        id: User's unique identifier
        email: User's email address
        google_id: Google account ID (if linked)
        full_name: User's full name
        profile_picture_url: Profile picture URL
        role: User role
        company_id: Company ID
        can_add_devices: Device permission
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp

    Example Response:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "full_name": "John Doe",
            "role": "user",
            "company_id": "456e7890-e89b-12d3-a456-426614174000",
            "can_add_devices": true,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """

    id: uuid.UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    google_id: Optional[str] = Field(None, description="Google account ID")
    full_name: str = Field(..., description="User's full name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    role: str = Field(..., description="User role")
    company_id: Optional[uuid.UUID] = Field(None, description="Company ID")
    can_add_devices: bool = Field(..., description="Can add devices permission")
    is_active: bool = Field(..., description="Account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLAlchemy models (Pydantic v2)
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com",
                "google_id": "1234567890",
                "full_name": "John Doe",
                "profile_picture_url": "https://example.com/photo.jpg",
                "role": "user",
                "company_id": "456e7890-e89b-12d3-a456-426614174000",
                "can_add_devices": True,
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-20T14:25:00Z"
            }
        }


# ============================================================
# User List Response Schema
# ============================================================

class UserListResponse(BaseModel):
    """
    Schema for paginated list of users.

    This schema wraps a list of users with pagination metadata.

    Fields:
        total: Total number of users
        page: Current page number
        page_size: Number of users per page
        users: List of user objects

    Example Response:
        {
            "total": 45,
            "page": 1,
            "page_size": 20,
            "users": [
                {user1}, {user2}, ...
            ]
        }
    """

    total: int = Field(..., description="Total number of users", example=45)
    page: int = Field(..., description="Current page number", example=1)
    page_size: int = Field(..., description="Users per page", example=20)
    users: List[UserResponse] = Field(..., description="List of users")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "total": 45,
                "page": 1,
                "page_size": 20,
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user1@example.com",
                        "full_name": "User One",
                        "role": "user",
                        "company_id": "456e7890-e89b-12d3-a456-426614174000",
                        "can_add_devices": True,
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        }
