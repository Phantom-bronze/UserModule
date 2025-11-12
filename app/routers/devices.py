"""
Device Management Router
========================

Handles Smart TV device operations:
- Device pairing with 4-digit codes
- Device linking to users
- Device status monitoring
- Device management (list, update, delete)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import random
import string

from app.database import get_db
from app.models.user import User
from app.models.device import Device
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-code", summary="Generate device pairing code")
async def generate_device_code(
    device_id: str,
    device_name: str,
    db: Session = Depends(get_db)
):
    """
    Generate a 4-digit pairing code for a device.

    The device (Smart TV) calls this to get a pairing code that
    users will enter to link the device to their account.
    """
    # Generate 4-digit code
    code = ''.join(random.choices(string.digits, k=4))

    # Check if device exists
    device = db.query(Device).filter(Device.device_id == device_id).first()

    if device:
        # Update existing device
        device.device_code = code
        device.device_name = device_name
        device.is_online = True
    else:
        # Create new device
        device = Device(
            device_id=device_id,
            device_name=device_name,
            device_code=code,
            is_online=True,
            is_linked=False
        )
        db.add(device)

    db.commit()
    db.refresh(device)

    logger.info(f"Generated pairing code for device: {device_id}")

    return {
        "device_id": device_id,
        "device_code": code,
        "expires_in_minutes": 15
    }


@router.post("/link", summary="Link device to user account")
async def link_device(
    device_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Link a device to the current user's account using the pairing code.
    """
    # Check if user can add devices
    if not current_user.can_add_devices:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add devices"
        )

    # Find device by code
    device = db.query(Device).filter(Device.device_code == device_code).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid device code"
        )

    if device.is_linked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device is already linked to an account"
        )

    # Link device to user
    device.user_id = current_user.id
    device.company_id = current_user.company_id
    device.is_linked = True
    device.device_code = None  # Clear the code

    db.commit()
    db.refresh(device)

    logger.info(f"Device linked: {device.device_id} to user {current_user.email}")

    return {
        "message": "Device linked successfully",
        "device_id": str(device.id),
        "device_name": device.device_name
    }


@router.get("/my-devices", summary="Get current user's devices")
async def get_my_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all devices linked to the current user.
    """
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()

    return [
        {
            "id": str(device.id),
            "device_id": device.device_id,
            "device_name": device.device_name,
            "is_online": device.is_online,
            "is_linked": device.is_linked,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None,
            "created_at": device.created_at.isoformat() if device.created_at else None
        }
        for device in devices
    ]


@router.delete("/{device_id}", summary="Unlink/delete device")
async def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unlink and delete a device.
    """
    device = db.query(Device).filter(
        Device.id == device_id,
        Device.user_id == current_user.id
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    db.delete(device)
    db.commit()

    logger.info(f"Device deleted: {device.device_id} by {current_user.email}")

    return {"message": "Device deleted successfully"}
