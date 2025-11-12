"""
Company Pydantic Schemas
========================

Schemas for Company-related API operations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""

    name: str = Field(..., min_length=2, max_length=255, description="Company name")
    subdomain: Optional[str] = Field(None, max_length=100, description="Unique subdomain")
    logo_url: Optional[str] = Field(None, description="Company logo URL")
    max_users: int = Field(default=10, ge=1, description="Maximum users allowed")
    max_devices: int = Field(default=5, ge=1, description="Maximum devices allowed")

    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format (alphanumeric and hyphens only)."""
        if v and not v.replace('-', '').isalnum():
            raise ValueError("Subdomain must contain only letters, numbers, and hyphens")
        return v.lower() if v else None

    class Config:
        schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "subdomain": "acme",
                "max_users": 50,
                "max_devices": 100
            }
        }


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    subdomain: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_devices: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format (alphanumeric and hyphens only)."""
        if v and not v.replace('-', '').isalnum():
            raise ValueError("Subdomain must contain only letters, numbers, and hyphens")
        return v.lower() if v else None


class CompanyResponse(BaseModel):
    """Schema for company data in API responses."""

    id: uuid.UUID
    name: str
    subdomain: Optional[str]
    logo_url: Optional[str]
    is_active: bool
    max_users: int
    max_devices: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CompanyListResponse(BaseModel):
    """Schema for company list item with statistics."""

    id: str
    name: str
    subdomain: Optional[str]
    logo_url: Optional[str]
    is_active: bool
    max_users: int
    max_devices: int
    current_users: int
    current_devices: int
    created_at: Optional[str]
    updated_at: Optional[str]


class CompanyStatsResponse(BaseModel):
    """Schema for company statistics."""

    company_id: str
    company_name: str
    users: dict
    devices: dict

    class Config:
        schema_extra = {
            "example": {
                "company_id": "550e8400-e29b-41d4-a716-446655440000",
                "company_name": "Acme Corporation",
                "users": {
                    "total": 25,
                    "active": 23,
                    "admins": 2,
                    "max_allowed": 50,
                    "remaining": 25
                },
                "devices": {
                    "total": 45,
                    "online": 42,
                    "linked": 40,
                    "max_allowed": 100,
                    "remaining": 55
                }
            }
        }
