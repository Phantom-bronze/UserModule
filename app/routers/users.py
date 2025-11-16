"""
User Management Router
======================

Handles user management operations:
- List users (with filtering)
- Get user details
- Update user permissions
- Delete/deactivate users
- Manage user roles

Permissions:
- Super Admin: Can manage all users
- Admin: Can manage users in their company (except other admins)
- User: Can only view/update their own profile
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserPermissionsUpdate,
    UserListResponse
)
from app.utils.auth import (
    get_current_user,
    require_admin,
    require_super_admin,
    check_company_access
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# User Creation
# ============================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user"
)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Create a new user (Super Admin only).

    This endpoint allows super admins to create users directly without
    going through the invitation process. The user will be created with
    the specified role and company.

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current super admin user

    Returns:
        UserResponse: Created user details

    Raises:
        HTTPException 400: If email already exists or validation fails
        HTTPException 403: If not a super admin
        HTTPException 404: If company not found
    """
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Validate company exists if company_id is provided
    if user_data.company_id:
        company = db.query(Company).filter(Company.id == user_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Check if company can add more users
        if not company.can_add_user():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company has reached maximum user limit ({company.max_users})"
            )

    try:
        # Create new user
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            company_id=user_data.company_id,
            can_add_devices=user_data.can_add_devices,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User created: {new_user.email} by {current_user.email}")

        return new_user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


# ============================================================
# User Listing and Retrieval
# ============================================================

@router.get(
    "",
    response_model=List[UserResponse],
    summary="List users"
)
async def list_users(
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    List users with optional filters.

    Super admins can list all users across all companies.
    Admins can only list users in their own company.

    Args:
        company_id: Filter by company (super admin only)
        role: Filter by user role
        is_active: Filter by active status
        skip: Pagination offset
        limit: Maximum results
        db: Database session
        current_user: Current user

    Returns:
        List[UserResponse]: List of users
    """
    query = db.query(User)

    # Apply company filter based on role
    if current_user.role == UserRole.SUPER_ADMIN:
        if company_id:
            query = query.filter(User.company_id == company_id)
    else:
        # Admins can only see their company's users
        query = query.filter(User.company_id == current_user.company_id)

    # Apply additional filters
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get users
    users = query.offset(skip).limit(limit).all()

    # Return users directly (FastAPI will serialize using UserResponse schema)
    return users


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's own profile.

    Returns detailed information about the authenticated user.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: User profile information
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user details by ID.

    Super admins can view any user.
    Admins can view users in their company.
    Users can only view their own profile.

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current user

    Returns:
        UserResponse: User details

    Raises:
        HTTPException 404: If user not found
        HTTPException 403: If no access permission
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check access permissions
    if current_user.role == UserRole.SUPER_ADMIN:
        pass  # Can view anyone
    elif current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this user"
            )
    else:
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )

    return user


# ============================================================
# User Updates
# ============================================================

@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update own profile"
)
async def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's own profile.

    Users can update their own name and profile picture.
    They cannot change their role or permissions.

    Args:
        user_data: Updated user data
        db: Database session
        current_user: Current user

    Returns:
        UserResponse: Updated user profile
    """
    try:
        # Only allow updating certain fields
        if user_data.full_name:
            current_user.full_name = user_data.full_name
        if user_data.profile_picture_url:
            current_user.profile_picture_url = user_data.profile_picture_url

        db.commit()
        db.refresh(current_user)

        logger.info(f"User updated own profile: {current_user.email}")

        return current_user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user (Admin only)"
)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Update user information (Admin only).

    Super admins can update any user.
    Admins can update users in their company (except other admins).

    Args:
        user_id: User UUID
        user_data: Updated user data
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Updated user details

    Raises:
        HTTPException 404: If user not found
        HTTPException 403: If no permission to update
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user can manage this user
    if not current_user.can_manage_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this user"
        )

    try:
        # Update allowed fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field not in ['role', 'company_id']:  # Restrict sensitive fields
                setattr(user, field, value)

        db.commit()
        db.refresh(user)

        logger.info(f"User updated: {user.email} by {current_user.email}")

        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.put(
    "/{user_id}/permissions",
    response_model=UserResponse,
    summary="Update user permissions"
)
async def update_user_permissions(
    user_id: uuid.UUID,
    permissions: UserPermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Update user permissions (Admin only).

    Admins can grant/revoke device management permissions for users
    in their company.

    Args:
        user_id: User UUID
        permissions: Updated permissions
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Updated user with new permissions

    Raises:
        HTTPException 404: If user not found
        HTTPException 403: If no permission
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check management permission
    if not current_user.can_manage_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this user's permissions"
        )

    try:
        user.can_add_devices = permissions.can_add_devices

        db.commit()
        db.refresh(user)

        logger.info(f"User permissions updated: {user.email} by {current_user.email}")

        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permissions"
        )


# ============================================================
# User Deactivation and Deletion
# ============================================================

@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user"
)
async def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Deactivate a user (Admin only).

    Deactivated users cannot log in but their data is preserved.

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Deactivated user details
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not current_user.can_manage_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to deactivate this user"
        )

    try:
        user.is_active = False

        db.commit()
        db.refresh(user)

        logger.info(f"User deactivated: {user.email} by {current_user.email}")

        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user"
)
async def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Activate a previously deactivated user (Admin only).

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current admin user

    Returns:
        UserResponse: Activated user details
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not current_user.can_manage_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to activate this user"
        )

    try:
        user.is_active = True

        db.commit()
        db.refresh(user)

        logger.info(f"User activated: {user.email} by {current_user.email}")

        return user

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to activate user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Delete a user permanently (Admin only).

    WARNING: This permanently deletes the user and all associated data.
    Consider deactivating instead.

    Args:
        user_id: User UUID
        db: Database session
        current_user: Current admin user

    Raises:
        HTTPException 404: If user not found
        HTTPException 403: If no permission
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not current_user.can_manage_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this user"
        )

    try:
        db.delete(user)
        db.commit()

        logger.warning(f"User deleted: {user.email} by {current_user.email}")

        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
