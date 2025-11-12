"""
Google Drive Integration Router
================================

Handles Google Drive connectivity:
- Link Google Drive account
- Manage Drive credentials
- List Drive files
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/connect", summary="Connect Google Drive")
async def connect_google_drive(
    auth_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Connect user's Google Drive account.

    The user must first authenticate with Google and provide the auth code.
    """
    # TODO: Implement Google Drive OAuth flow
    # 1. Exchange auth code for tokens
    # 2. Store tokens in google_drive_tokens table (encrypted)
    # 3. Verify access to Drive

    logger.info(f"Google Drive connect requested by {current_user.email}")

    return {
        "message": "Google Drive connection initiated",
        "status": "pending_implementation"
    }


@router.get("/status", summary="Get Google Drive connection status")
async def get_drive_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if user's Google Drive is connected.
    """
    # TODO: Check if user has valid Drive tokens

    return {
        "connected": False,
        "email": None
    }


@router.delete("/disconnect", summary="Disconnect Google Drive")
async def disconnect_google_drive(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Disconnect user's Google Drive account.
    """
    # TODO: Delete Drive tokens

    logger.info(f"Google Drive disconnected by {current_user.email}")

    return {"message": "Google Drive disconnected"}
