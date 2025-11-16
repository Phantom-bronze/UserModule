"""
Pydantic Schemas Package
=========================

This package contains Pydantic models (schemas) for API request/response validation.

Schemas define:
- Request body structure and validation rules
- Response format and data types
- Data transformation and serialization
- Input sanitization and type checking

Using Pydantic provides:
- Automatic data validation
- Clear API documentation (via FastAPI)
- Type safety
- Error messages for invalid data
- Data serialization/deserialization

Schema Types:
- BaseModel: For request bodies
- Response models: For API responses
- Create models: For creating new resources
- Update models: For updating existing resources (partial)
"""

# Import all schemas for easy access
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)

from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse
)

from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationAccept
)

from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    GoogleAuthRequest
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",

    # Company schemas
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyListResponse",

    # Invitation schemas
    "InvitationCreate",
    "InvitationResponse",
    "InvitationAccept",

    # Auth schemas
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "GoogleAuthRequest",
]
