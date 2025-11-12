"""
Invitation Router
=================

Handles user invitation system:
- Send invitations to new users
- List pending invitations
- Accept/decline invitations
- Cancel invitations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets
import uuid

from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.utils.auth import get_current_user, require_admin
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def send_invitation(
    invitation_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Send an invitation to a new user (Admin only).

    The invited user will receive an email with a link to accept the invitation.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == invitation_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Check if there's already a pending invitation
    pending = db.query(Invitation).filter(
        Invitation.email == invitation_data.email,
        Invitation.status == "pending"
    ).first()
    if pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation already sent to this email"
        )

    # Generate invitation token
    token = secrets.token_urlsafe(32)

    # Create invitation
    invitation = Invitation(
        email=invitation_data.email,
        role=invitation_data.role,
        company_id=current_user.company_id,
        invited_by=current_user.id,
        token=token,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=settings.INVITATION_TOKEN_EXPIRE_HOURS)
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # TODO: Send invitation email
    logger.info(f"Invitation sent to {invitation_data.email} by {current_user.email}")

    return invitation


@router.get("", summary="List invitations")
async def list_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    List all invitations for the current user's company.
    """
    invitations = db.query(Invitation).filter(
        Invitation.company_id == current_user.company_id
    ).all()

    return invitations


@router.delete("/{invitation_id}", summary="Cancel invitation")
async def cancel_invitation(
    invitation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin())
):
    """
    Cancel a pending invitation.
    """
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.company_id == current_user.company_id
    ).first()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    invitation.status = "cancelled"
    db.commit()

    logger.info(f"Invitation cancelled: {invitation.email} by {current_user.email}")

    return {"message": "Invitation cancelled"}
