"""
Company Management Router
=========================

Handles company/organization management operations.
Only super admins can create, update, or delete companies.

Endpoints:
- POST /companies - Create new company
- GET /companies - List all companies
- GET /companies/{id} - Get company details
- PUT /companies/{id} - Update company
- DELETE /companies/{id} - Delete company
- GET /companies/{id}/users - List company users
- GET /companies/{id}/devices - List company devices
- GET /companies/{id}/stats - Get company statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.device import Device
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
    CompanyStatsResponse
)
from app.utils.auth import (
    get_current_user,
    require_super_admin,
    require_admin,
    check_company_access
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Company CRUD Operations
# ============================================================

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new company"
)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Create a new company (Super Admin only).

    This endpoint creates a new company/organization in the system.
    After creating a company, the super admin should invite an admin
    to manage it.

    Args:
        company_data: Company creation data
        db: Database session
        current_user: Current super admin user

    Returns:
        CompanyResponse: Created company details

    Raises:
        HTTPException 409: If subdomain already exists
        HTTPException 403: If user is not super admin
    """
    # Check if subdomain already exists
    if company_data.subdomain:
        existing = db.query(Company).filter(
            Company.subdomain == company_data.subdomain
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Subdomain '{company_data.subdomain}' is already taken"
            )

    try:
        # Create company
        company = Company(
            name=company_data.name,
            subdomain=company_data.subdomain,
            logo_url=company_data.logo_url,
            max_users=company_data.max_users,
            max_devices=company_data.max_devices,
            is_active=True
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        logger.info(f"Company created: {company.name} by {current_user.email}")

        return company

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create company"
        )


@router.get(
    "",
    response_model=List[CompanyListResponse],
    summary="List all companies"
)
async def list_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    List all companies (Super Admin only).

    Returns a paginated list of all companies in the system with
    basic information and statistics.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum records to return (pagination)
        is_active: Filter by active status
        db: Database session
        current_user: Current super admin user

    Returns:
        List[CompanyListResponse]: List of companies
    """
    query = db.query(Company)

    # Apply filters
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)

    # Get companies
    companies = query.offset(skip).limit(limit).all()

    # Add user and device counts
    result = []
    for company in companies:
        users_count = db.query(User).filter(User.company_id == company.id).count()
        devices_count = db.query(Device).filter(Device.company_id == company.id).count()

        result.append({
            "id": str(company.id),
            "name": company.name,
            "subdomain": company.subdomain,
            "logo_url": company.logo_url,
            "is_active": company.is_active,
            "max_users": company.max_users,
            "max_devices": company.max_devices,
            "current_users": users_count,
            "current_devices": devices_count,
            "created_at": company.created_at.isoformat() if company.created_at else None,
            "updated_at": company.updated_at.isoformat() if company.updated_at else None
        })

    return result


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get company details"
)
async def get_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Get detailed company information.

    Super admins can access any company.
    Admins can only access their own company.

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current user

    Returns:
        CompanyResponse: Company details

    Raises:
        HTTPException 404: If company not found
        HTTPException 403: If user doesn't have access
    """
    # Check access
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return company


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update company"
)
async def update_company(
    company_id: uuid.UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Update company information (Super Admin only).

    Args:
        company_id: Company UUID
        company_data: Updated company data
        db: Database session
        current_user: Current super admin user

    Returns:
        CompanyResponse: Updated company details

    Raises:
        HTTPException 404: If company not found
        HTTPException 409: If new subdomain already exists
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    try:
        # Check subdomain uniqueness if being updated
        if company_data.subdomain and company_data.subdomain != company.subdomain:
            existing = db.query(Company).filter(
                Company.subdomain == company_data.subdomain,
                Company.id != company_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Subdomain '{company_data.subdomain}' is already taken"
                )

        # Update fields
        update_data = company_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)

        logger.info(f"Company updated: {company.name} by {current_user.email}")

        return company

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update company"
        )


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company"
)
async def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Delete a company (Super Admin only).

    WARNING: This will cascade delete all users, devices, and content
    associated with the company. Use with caution!

    Consider deactivating the company instead.

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current super admin user

    Raises:
        HTTPException 404: If company not found
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    try:
        db.delete(company)
        db.commit()

        logger.warning(f"Company deleted: {company.name} by {current_user.email}")

        return None

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete company"
        )


# ============================================================
# Company Operations
# ============================================================

@router.post(
    "/{company_id}/deactivate",
    response_model=CompanyResponse,
    summary="Deactivate company"
)
async def deactivate_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Deactivate a company (Super Admin only).

    This deactivates the company and all its users and devices.
    Data is preserved and can be reactivated later.

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current super admin user

    Returns:
        CompanyResponse: Deactivated company details
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    try:
        company.deactivate(db)
        db.refresh(company)

        logger.info(f"Company deactivated: {company.name} by {current_user.email}")

        return company

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate company"
        )


@router.post(
    "/{company_id}/activate",
    response_model=CompanyResponse,
    summary="Activate company"
)
async def activate_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin())
):
    """
    Activate a company (Super Admin only).

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current super admin user

    Returns:
        CompanyResponse: Activated company details
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    try:
        company.activate(db)
        db.refresh(company)

        logger.info(f"Company activated: {company.name} by {current_user.email}")

        return company

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to activate company: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate company"
        )


@router.get(
    "/{company_id}/stats",
    response_model=CompanyStatsResponse,
    summary="Get company statistics"
)
async def get_company_stats(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Get company statistics and usage information.

    Args:
        company_id: Company UUID
        db: Database session
        current_user: Current user

    Returns:
        CompanyStatsResponse: Company statistics

    Raises:
        HTTPException 404: If company not found
        HTTPException 403: If user doesn't have access
    """
    # Check access
    if not check_company_access(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this company"
        )

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Get statistics
    total_users = db.query(User).filter(User.company_id == company_id).count()
    active_users = db.query(User).filter(
        User.company_id == company_id,
        User.is_active == True
    ).count()
    admin_users = db.query(User).filter(
        User.company_id == company_id,
        User.role == UserRole.ADMIN
    ).count()

    total_devices = db.query(Device).filter(Device.company_id == company_id).count()
    online_devices = db.query(Device).filter(
        Device.company_id == company_id,
        Device.is_online == True
    ).count()
    linked_devices = db.query(Device).filter(
        Device.company_id == company_id,
        Device.is_linked == True
    ).count()

    return {
        "company_id": str(company_id),
        "company_name": company.name,
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
            "max_allowed": company.max_users,
            "remaining": company.max_users - total_users
        },
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "linked": linked_devices,
            "max_allowed": company.max_devices,
            "remaining": company.max_devices - total_devices
        }
    }
