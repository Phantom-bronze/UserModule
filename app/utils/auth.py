"""
Authentication Utilities
========================

This module provides functions for authentication and authorization:
- JWT token creation and validation
- User authentication from tokens
- Role-based access control decorators
- Password hashing and verification

JWT Token Structure:
- Access Token: Short-lived (30 minutes), used for API requests
- Refresh Token: Long-lived (7 days), used to get new access tokens

Token Payload:
{
    "sub": "user_id",  # Subject (user ID)
    "email": "user@example.com",
    "role": "admin",
    "company_id": "company_uuid",
    "type": "access",  # or "refresh"
    "exp": timestamp,  # Expiration time
    "iat": timestamp   # Issued at time
}

Security Features:
- HMAC-SHA256 signing
- Configurable expiration times
- Role-based access control
- Token type validation (access vs refresh)
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid
import logging

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

# ============================================================
# Logger Configuration
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# OAuth2 Configuration
# ============================================================

# OAuth2 password bearer for token extraction from requests
# This extracts the token from the Authorization header: "Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============================================================
# Token Creation Functions
# ============================================================

def create_access_token(user_id: uuid.UUID, email: str, role: str,
                       company_id: Optional[uuid.UUID] = None) -> str:
    """
    Create a JWT access token for authenticated user.

    Access tokens are short-lived and used for API authentication.
    They should be included in the Authorization header of requests.

    Args:
        user_id: User's unique identifier
        email: User's email address
        role: User's role (super_admin, admin, or user)
        company_id: User's company ID (optional, None for super_admin)

    Returns:
        str: JWT access token

    Example:
        >>> token = create_access_token(
        >>>     user_id=user.id,
        >>>     email=user.email,
        >>>     role=user.role,
        >>>     company_id=user.company_id
        >>> )
        >>> # Client includes in requests: Authorization: Bearer <token>
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    # Token payload
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "role": role,
        "company_id": str(company_id) if company_id else None,
        "type": "access",
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    }

    # Encode and sign the token
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(user_id: uuid.UUID, email: str) -> str:
    """
    Create a JWT refresh token for obtaining new access tokens.

    Refresh tokens are long-lived and used to obtain new access tokens
    without requiring the user to log in again.

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        str: JWT refresh token

    Example:
        >>> refresh_token = create_refresh_token(
        >>>     user_id=user.id,
        >>>     email=user.email
        >>> )
        >>> # Client stores securely and uses to refresh access token
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta

    # Token payload (minimal for refresh tokens)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    # Encode and sign the token
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# ============================================================
# Token Validation Functions
# ============================================================

def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verify and decode a JWT token.

    This function:
    1. Decodes the token
    2. Verifies the signature
    3. Checks expiration
    4. Validates token type

    Args:
        token: JWT token string
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or wrong type

    Example:
        >>> try:
        >>>     payload = verify_token(token, "access")
        >>>     user_id = payload["sub"]
        >>> except HTTPException:
        >>>     # Token invalid
        >>>     pass
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Verify token type
        token_type = payload.get("type")
        if token_type != expected_type:
            logger.warning(f"Invalid token type: expected {expected_type}, got {token_type}")
            raise credentials_exception

        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return payload

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception


# ============================================================
# User Authentication Functions
# ============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    This function is used as a FastAPI dependency to extract
    and validate the current user from the request token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found

    Example:
        >>> from fastapi import Depends
        >>> from app.utils.auth import get_current_user
        >>>
        >>> @app.get("/profile")
        >>> async def get_profile(current_user: User = Depends(get_current_user)):
        >>>     return {"email": current_user.email, "name": current_user.full_name}
    """
    # Verify token and get payload
    payload = verify_token(token, "access")

    # Extract user ID from payload
    user_id_str = payload.get("sub")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user (alias for get_current_user).

    This is kept for semantic clarity - it's clear that we're checking
    for active users.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User: Current active user object

    Example:
        >>> @app.get("/dashboard")
        >>> async def dashboard(user: User = Depends(get_current_active_user)):
        >>>     return {"message": f"Welcome, {user.full_name}!"}
    """
    return current_user


# ============================================================
# Role-Based Access Control Functions
# ============================================================

def require_role(allowed_roles: list[UserRole]):
    """
    Decorator factory for role-based access control.

    Creates a dependency that checks if the current user has one of
    the allowed roles. Use this to restrict endpoints to specific roles.

    Args:
        allowed_roles: List of allowed UserRole values

    Returns:
        Function: Dependency function for FastAPI

    Example:
        >>> from app.models.user import UserRole
        >>> from app.utils.auth import require_role
        >>>
        >>> # Only super admins can access this endpoint
        >>> @app.post("/companies")
        >>> async def create_company(
        >>>     user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
        >>> ):
        >>>     # Only super admins reach here
        >>>     pass
        >>>
        >>> # Admins and super admins can access this endpoint
        >>> @app.get("/users")
        >>> async def list_users(
        >>>     user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ADMIN]))
        >>> ):
        >>>     # Only admins and super admins reach here
        >>>     pass
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Check if current user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            User: Current user if role check passes

        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


def require_super_admin():
    """
    Dependency that requires super admin role.

    Convenience function for endpoints that only super admins can access.

    Returns:
        Function: Dependency function for FastAPI

    Example:
        >>> @app.delete("/companies/{company_id}")
        >>> async def delete_company(
        >>>     company_id: UUID,
        >>>     user: User = Depends(require_super_admin())
        >>> ):
        >>>     # Only super admins can delete companies
        >>>     pass
    """
    return require_role([UserRole.SUPER_ADMIN])


def require_admin():
    """
    Dependency that requires admin or super admin role.

    Returns:
        Function: Dependency function for FastAPI

    Example:
        >>> @app.post("/users")
        >>> async def create_user(
        >>>     user_data: dict,
        >>>     user: User = Depends(require_admin())
        >>> ):
        >>>     # Only admins and super admins can create users
        >>>     pass
    """
    return require_role([UserRole.SUPER_ADMIN, UserRole.ADMIN])


# ============================================================
# Company Access Control
# ============================================================

def check_company_access(user: User, company_id: uuid.UUID) -> bool:
    """
    Check if user has access to a specific company's data.

    Access rules:
    - Super admins have access to all companies
    - Admins and users have access only to their own company

    Args:
        user: User making the request
        company_id: Company ID to check access for

    Returns:
        bool: True if user has access, False otherwise

    Example:
        >>> if not check_company_access(current_user, company_id):
        >>>     raise HTTPException(status_code=403, detail="Access denied")
    """
    # Super admins have access to everything
    if user.role == UserRole.SUPER_ADMIN:
        return True

    # Others can only access their own company
    return user.company_id == company_id


def require_company_access(company_id: uuid.UUID):
    """
    Dependency factory that checks company access.

    Args:
        company_id: Company ID to check access for

    Returns:
        Function: Dependency function for FastAPI

    Example:
        >>> @app.get("/companies/{company_id}/users")
        >>> async def list_company_users(
        >>>     company_id: UUID,
        >>>     user: User = Depends(require_company_access(company_id))
        >>> ):
        >>>     # User has access to this company
        >>>     pass
    """
    async def company_access_checker(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has access to the company."""
        if not check_company_access(current_user, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company's data"
            )
        return current_user

    return company_access_checker


# ============================================================
# Token Response Helper
# ============================================================

def create_token_response(user: User) -> dict:
    """
    Create a complete token response for user login.

    This function creates both access and refresh tokens and
    returns them in a standardized format.

    Args:
        user: User object to create tokens for

    Returns:
        dict: Token response with access_token, refresh_token, and user info

    Example:
        >>> user = db.query(User).filter(User.email == email).first()
        >>> token_response = create_token_response(user)
        >>> return JSONResponse(content=token_response)
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": "uuid",
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "admin"
            }
        }
    """
    # Create tokens
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
        company_id=user.company_id
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        email=user.email
    )

    # Return standardized response
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # In seconds
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "company_id": str(user.company_id) if user.company_id else None,
            "can_add_devices": user.can_add_devices
        }
    }


# ============================================================
# Token Refresh
# ============================================================

async def refresh_access_token(
    refresh_token: str,
    db: Session
) -> dict:
    """
    Create a new access token from a refresh token.

    Args:
        refresh_token: Valid refresh token
        db: Database session

    Returns:
        dict: New token response

    Raises:
        HTTPException: If refresh token is invalid

    Example:
        >>> @app.post("/auth/refresh")
        >>> async def refresh_token(
        >>>     refresh_token: str,
        >>>     db: Session = Depends(get_db)
        >>> ):
        >>>     return await refresh_access_token(refresh_token, db)
    """
    # Verify refresh token
    payload = verify_token(refresh_token, "refresh")

    # Get user from database
    user_id_str = payload.get("sub")
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new token response
    return create_token_response(user)
