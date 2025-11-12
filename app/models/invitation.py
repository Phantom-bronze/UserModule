"""
Invitation Model
================

This module defines the Invitation model for tracking user invitations.

The invitation system works as follows:
1. Super Admin invites Admin users to companies
2. Admin users invite regular Users to their company
3. Each invitation has a unique token sent via email
4. Invitations expire after a configurable time period
5. When accepted, the invitation creates a new user account

This ensures secure user onboarding with proper authorization checks.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import secrets
import enum

from app.database import Base
from app.config import settings


class InvitationStatus(str, enum.Enum):
    """
    Enumeration of invitation statuses.

    Statuses:
        - PENDING: Invitation sent, waiting for user to accept
        - ACCEPTED: User accepted the invitation and created account
        - EXPIRED: Invitation expired before being accepted
        - CANCELLED: Invitation was cancelled by the sender

    Example:
        >>> invitation.status = InvitationStatus.PENDING
        >>> if invitation.is_expired():
        >>>     invitation.status = InvitationStatus.EXPIRED
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Invitation(Base):
    """
    Invitation Model Class

    Represents an invitation sent to a user to join the platform.
    Invitations are sent via email and contain a unique token for security.

    Attributes:
        id (UUID): Unique identifier for the invitation (Primary Key)
        email (str): Email address of the invitee (required)
        role (str): Role to be assigned (admin or user)
        company_id (UUID): Company the invitee will belong to (Foreign Key)
        invited_by (UUID): User who sent the invitation (Foreign Key)
        token (str): Unique token for the invitation link (Unique)
        status (InvitationStatus): Current status of the invitation
        expires_at (datetime): Expiration timestamp
        created_at (datetime): Timestamp when invitation was created
        accepted_at (datetime): Timestamp when invitation was accepted (if accepted)

    Relationships:
        company: The company this invitation is for (Many-to-One with Company)
        invited_by_user: The user who sent this invitation (Many-to-One with User)

    Database Table: invitations

    Business Rules:
        - Super admins can invite admins to any company
        - Admins can invite users to their own company
        - Invitations expire after INVITATION_TOKEN_EXPIRE_HOURS
        - Each invitation can only be accepted once
        - Email addresses must be unique per company (cannot invite twice)

    Example:
        >>> # Create an invitation
        >>> invitation = Invitation(
        >>>     email="newuser@example.com",
        >>>     role="user",
        >>>     company_id=company.id,
        >>>     invited_by=admin.id
        >>> )
        >>> db.add(invitation)
        >>> db.commit()
        >>>
        >>> # Send invitation email with token
        >>> send_invitation_email(invitation.email, invitation.token)
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "invitations"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the invitation"
    )

    # ========================================
    # Invitation Details
    # ========================================
    email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Email address of the invitee"
    )

    role = Column(
        String(50),
        nullable=False,
        comment="Role to be assigned (admin or user)"
    )

    # ========================================
    # Company Relationship
    # ========================================
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Company the invitee will belong to"
    )

    # ========================================
    # Invited By
    # ========================================
    invited_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who sent the invitation"
    )

    # ========================================
    # Security Token
    # ========================================
    token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: secrets.token_urlsafe(32),
        comment="Unique secure token for the invitation link"
    )

    # ========================================
    # Status
    # ========================================
    status = Column(
        SQLEnum(InvitationStatus),
        default=InvitationStatus.PENDING,
        nullable=False,
        index=True,
        comment="Current status of the invitation"
    )

    # ========================================
    # Timestamps
    # ========================================
    expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(
            hours=settings.INVITATION_TOKEN_EXPIRE_HOURS
        ),
        comment="Expiration timestamp for the invitation"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when the invitation was created"
    )

    accepted_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when the invitation was accepted"
    )

    # ========================================
    # Relationships
    # ========================================

    # Many-to-One: Invitation belongs to one Company
    company = relationship(
        "Company",
        back_populates="invitations",
        lazy="joined"
    )

    # Many-to-One: Invitation sent by one User
    invited_by_user = relationship(
        "User",
        back_populates="invitations_sent",
        foreign_keys=[invited_by],
        lazy="joined"
    )

    # ========================================
    # Model Methods
    # ========================================

    def is_expired(self) -> bool:
        """
        Check if the invitation has expired.

        Returns:
            bool: True if invitation is expired, False otherwise
        """
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """
        Check if the invitation is valid (pending and not expired).

        Returns:
            bool: True if invitation is valid, False otherwise
        """
        return (
            self.status == InvitationStatus.PENDING
            and not self.is_expired()
        )

    def mark_as_accepted(self):
        """
        Mark the invitation as accepted.

        Updates the status to ACCEPTED and sets the accepted_at timestamp.
        """
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = datetime.utcnow()

    def mark_as_expired(self):
        """
        Mark the invitation as expired.

        Updates the status to EXPIRED.
        """
        self.status = InvitationStatus.EXPIRED

    def mark_as_cancelled(self):
        """
        Mark the invitation as cancelled.

        Updates the status to CANCELLED.
        """
        self.status = InvitationStatus.CANCELLED

    def get_invitation_url(self, base_url: str) -> str:
        """
        Generate the full invitation URL.

        Args:
            base_url: Base URL of the application (e.g., "https://app.example.com")

        Returns:
            str: Full invitation URL with token

        Example:
            >>> url = invitation.get_invitation_url("https://app.example.com")
            >>> print(url)
            'https://app.example.com/accept-invitation?token=abc123...'
        """
        return f"{base_url}/accept-invitation?token={self.token}"

    def time_until_expiry(self) -> timedelta:
        """
        Calculate time remaining until invitation expires.

        Returns:
            timedelta: Time remaining until expiration (can be negative if expired)
        """
        return self.expires_at - datetime.utcnow()

    @staticmethod
    def generate_secure_token() -> str:
        """
        Generate a secure random token for invitation.

        Returns:
            str: URL-safe random token
        """
        return secrets.token_urlsafe(32)

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the Invitation object.

        Returns:
            str: String representation showing key invitation information
        """
        return (
            f"<Invitation(id={self.id}, email='{self.email}', "
            f"role={self.role}, status={self.status.value})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Invitation email and status
        """
        return f"Invitation to {self.email} ({self.status.value})"
