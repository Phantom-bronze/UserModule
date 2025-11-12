"""
Authentication Pydantic Schemas
================================

Schemas for authentication-related API operations including:
- Login requests
- Token responses
- Google OAuth authentication
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid


class LoginRequest(BaseModel):
    """Schema for login request (email/password or Google OAuth code)."""

    email: Optional[EmailStr] = Field(None, description="Email for password login")
    password: Optional[str] = Field(None, description="Password for email login")
    google_auth_code: Optional[str] = Field(None, description="Google OAuth authorization code")

    class Config:
        schema_extra = {
            "example": {
                "google_auth_code": "4/0AX4XfWh..."
            }
        }


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth authentication."""

    code: str = Field(..., description="Google OAuth authorization code")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")


class TokenResponse(BaseModel):
    """Schema for token response after successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: dict = Field(..., description="User information")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "role": "user"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str = Field(..., description="Refresh token to get new access token")


class GoogleAuthURL(BaseModel):
    """Google OAuth authorization URL response."""

    auth_url: str = Field(
        ...,
        description="Google OAuth authorization URL to redirect user to"
    )

    class Config:
        schema_extra = {
            "example": {
                "auth_url": "https://accounts.google.com/o/oauth2/auth?client_id=..."
            }
        }
