"""
Invitation Pydantic Schemas
============================

Schemas for Invitation-related API operations.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class InvitationCreate(BaseModel):
    """Schema for creating a new invitation."""

    email: EmailStr = Field(..., description="Invitee's email address")
    role: str = Field(..., description="Role to assign (admin or user)")
    company_id: uuid.UUID = Field(..., description="Company to invite user to")

    class Config:
        schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "role": "user",
                "company_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation."""

    token: str = Field(..., description="Invitation token from email")
    full_name: str = Field(..., min_length=2, max_length=255, description="User's full name")

    class Config:
        schema_extra = {
            "example": {
                "token": "abc123xyz789",
                "full_name": "John Doe"
            }
        }


class InvitationResponse(BaseModel):
    """Schema for invitation data in API responses."""

    id: uuid.UUID
    email: str
    role: str
    company_id: uuid.UUID
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
