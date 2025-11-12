"""
Device Model
============

This module defines the Device model which represents Smart TV devices
in the digital signage system.

Devices (Smart TVs) are paired with user accounts using a 4-digit code:
1. TV app generates a random 4-digit code on first launch
2. User enters the code in mobile app to link the TV
3. Once linked, the TV displays content selected by the user
4. User can manage multiple TVs from their mobile app

The device model tracks:
- Connection status (online/offline)
- Link status (linked to user or waiting for pairing)
- Current playlist being displayed
- Last activity timestamp for offline detection
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import random

from app.database import Base
from app.config import settings


class Device(Base):
    """
    Device Model Class

    Represents a Smart TV device that displays digital signage content.
    Devices are linked to user accounts using a 4-digit pairing code.

    Attributes:
        id (UUID): Unique identifier for the device (Primary Key)
        user_id (UUID): User who owns this device (Foreign Key)
        company_id (UUID): Company this device belongs to (Foreign Key)
        device_name (str): Name given to the device by user (required)
        device_code (str): 4-digit pairing code (Unique, generated automatically)
        device_id (str): Unique device identifier from TV app (Unique, required)
        is_online (bool): Current online status
        is_linked (bool): Whether device is linked to a user
        current_playlist_id (UUID): Currently playing playlist (Foreign Key)
        last_seen (datetime): Last activity timestamp
        created_at (datetime): Device registration timestamp
        updated_at (datetime): Last update timestamp
        linked_at (datetime): When device was linked to user

    Relationships:
        user: The user who owns this device (Many-to-One with User)
        company: The company this device belongs to (Many-to-One with Company)

    Database Table: devices

    Business Rules:
        - Device code expires after DEVICE_CODE_EXPIRE_MINUTES
        - Device is marked offline if no heartbeat for DEVICE_OFFLINE_TIMEOUT_MINUTES
        - Users can add devices only if can_add_devices permission is true
        - Company device limit (max_devices) is enforced
        - Devices cannot be transferred between users (must unlink and re-link)

    Example:
        >>> # TV app generates pairing code
        >>> device = Device(
        >>>     device_id="unique-tv-id-123",
        >>>     device_name="Living Room TV"
        >>> )
        >>> db.add(device)
        >>> db.commit()
        >>> print(f"Pairing code: {device.device_code}")
        >>>
        >>> # User links the device
        >>> device.link_to_user(user.id, user.company_id)
        >>> db.commit()
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "devices"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the device"
    )

    # ========================================
    # User Relationship
    # ========================================
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,  # NULL until device is linked
        index=True,
        comment="User who owns this device"
    )

    # ========================================
    # Company Relationship
    # ========================================
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,  # NULL until device is linked
        index=True,
        comment="Company this device belongs to"
    )

    # ========================================
    # Device Information
    # ========================================
    device_name = Column(
        String(255),
        nullable=False,
        comment="Name given to the device by user"
    )

    device_code = Column(
        String(4),
        unique=True,
        nullable=True,
        index=True,
        comment="4-digit pairing code for linking device"
    )

    device_id = Column(
        String(255),
        unique=True,
        nullable=False,
        comment="Unique device identifier from TV app"
    )

    # ========================================
    # Device Status
    # ========================================
    is_online = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Current online status"
    )

    is_linked = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether device is linked to a user"
    )

    # ========================================
    # Current Playlist
    # ========================================
    current_playlist_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Currently playing playlist"
    )

    # ========================================
    # Timestamps
    # ========================================
    last_seen = Column(
        DateTime,
        nullable=True,
        comment="Last activity timestamp"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Device registration timestamp"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    linked_at = Column(
        DateTime,
        nullable=True,
        comment="When device was linked to user"
    )

    # ========================================
    # Relationships
    # ========================================

    # Many-to-One: Device belongs to one User
    user = relationship(
        "User",
        back_populates="devices",
        lazy="joined"
    )

    # Many-to-One: Device belongs to one Company
    company = relationship(
        "Company",
        back_populates="devices",
        lazy="joined"
    )

    # ========================================
    # Model Methods
    # ========================================

    @staticmethod
    def generate_device_code() -> str:
        """
        Generate a random 4-digit pairing code.

        Returns:
            str: 4-digit code as string (e.g., "1234")

        Example:
            >>> code = Device.generate_device_code()
            >>> print(code)  # "7392"
        """
        return str(random.randint(1000, 9999))

    def regenerate_code(self):
        """
        Regenerate a new pairing code for the device.

        This should be called when:
        - Device code expires
        - User requests a new code
        - Device is unlinked and needs to be re-paired
        """
        self.device_code = self.generate_device_code()
        self.is_linked = False

    def link_to_user(self, user_id: uuid.UUID, company_id: uuid.UUID):
        """
        Link the device to a user account.

        Args:
            user_id: UUID of the user
            company_id: UUID of the company

        Example:
            >>> device.link_to_user(user.id, user.company_id)
            >>> db.commit()
        """
        self.user_id = user_id
        self.company_id = company_id
        self.is_linked = True
        self.linked_at = datetime.utcnow()
        self.device_code = None  # Clear the code after linking

    def unlink_from_user(self):
        """
        Unlink the device from the user account.

        This generates a new pairing code so the device can be linked again.
        """
        self.user_id = None
        self.company_id = None
        self.is_linked = False
        self.linked_at = None
        self.current_playlist_id = None
        self.regenerate_code()

    def update_heartbeat(self):
        """
        Update the last_seen timestamp to indicate device is active.

        This should be called regularly by the TV app (e.g., every minute)
        to indicate the device is online and functioning.
        """
        self.last_seen = datetime.utcnow()
        self.is_online = True

    def check_if_offline(self) -> bool:
        """
        Check if device should be marked as offline based on last_seen timestamp.

        A device is considered offline if it hasn't sent a heartbeat within
        the DEVICE_OFFLINE_TIMEOUT_MINUTES period.

        Returns:
            bool: True if device should be marked offline, False otherwise
        """
        if not self.last_seen:
            return True

        timeout_minutes = settings.DEVICE_OFFLINE_TIMEOUT_MINUTES
        offline_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)

        return self.last_seen < offline_threshold

    def mark_offline_if_needed(self):
        """
        Mark device as offline if last_seen is too old.

        This should be called periodically (e.g., every minute) by a
        background task to update device status.
        """
        if self.check_if_offline():
            self.is_online = False

    def set_current_playlist(self, playlist_id: uuid.UUID):
        """
        Set the current playlist for this device.

        Args:
            playlist_id: UUID of the playlist to display
        """
        self.current_playlist_id = playlist_id

    def is_code_expired(self) -> bool:
        """
        Check if the device pairing code has expired.

        Returns:
            bool: True if code is expired, False otherwise
        """
        if not self.device_code or self.is_linked:
            return False

        expire_minutes = settings.DEVICE_CODE_EXPIRE_MINUTES
        code_age = datetime.utcnow() - self.created_at

        return code_age.total_seconds() > (expire_minutes * 60)

    def get_uptime(self) -> timedelta:
        """
        Calculate device uptime (time since last link).

        Returns:
            timedelta: Time since device was linked (or creation if not linked)
        """
        reference_time = self.linked_at if self.linked_at else self.created_at
        return datetime.utcnow() - reference_time

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the Device object.

        Returns:
            str: String representation showing key device information
        """
        return (
            f"<Device(id={self.id}, name='{self.device_name}', "
            f"linked={self.is_linked}, online={self.is_online})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Device name and status
        """
        status = "Online" if self.is_online else "Offline"
        linked = "Linked" if self.is_linked else f"Code: {self.device_code}"
        return f"{self.device_name} ({status}, {linked})"
