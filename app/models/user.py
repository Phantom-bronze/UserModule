"""
User Model
==========

This module defines the User model which represents user accounts in the system.

The application supports three types of users:
1. Super Admin: Can manage all companies, admins, and users across the entire system
2. Admin: Can manage users and settings within their company
3. User: Can manage their own content, playlists, and devices

Each user authenticates via Google SSO (Single Sign-On) and can:
- Link their Google Drive account to import content
- Create and manage playlists
- Link and control Smart TV devices
- Access features based on their role and permissions
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """
    Enumeration of user roles in the system.

    Roles define the level of access and permissions a user has:
    - SUPER_ADMIN: Full system access, can manage all companies and users
    - ADMIN: Company-level access, can manage users within their company
    - USER: Basic access, can manage own content and devices

    Example:
        >>> user = User(role=UserRole.ADMIN)
        >>> if user.role == UserRole.ADMIN:
        >>>     print("User is an admin")
    """
    SUPER_ADMIN = "super_admin"  # System-wide administrator
    ADMIN = "admin"              # Company administrator
    USER = "user"                # Regular user


class User(Base):
    """
    User Model Class

    Represents a user account in the system. Users authenticate via Google SSO
    and are assigned to roles that determine their permissions.

    Attributes:
        id (UUID): Unique identifier for the user (Primary Key)
        email (str): User's email address (Unique, required)
        google_id (str): Google account ID for SSO authentication (Unique)
        full_name (str): User's full name (required)
        profile_picture_url (str): URL to user's profile picture from Google
        role (UserRole): User's role (super_admin, admin, or user)
        company_id (UUID): Reference to the company the user belongs to (Foreign Key)
        can_add_devices (bool): Permission flag - whether user can add devices
        is_active (bool): Account status - whether the account is active
        created_at (datetime): Timestamp when the account was created
        updated_at (datetime): Timestamp when the account was last updated
        last_login (datetime): Timestamp of the user's last login

    Relationships:
        company: The company this user belongs to (Many-to-One with Company)
        devices: List of devices owned by this user (One-to-Many with Device)
        invitations_sent: Invitations sent by this user (One-to-Many with Invitation)
        audit_logs: Audit logs for actions performed by this user (One-to-Many)

    Database Table: users

    Example:
        >>> # Create a new user
        >>> user = User(
        >>>     email="john@example.com",
        >>>     google_id="123456789",
        >>>     full_name="John Doe",
        >>>     role=UserRole.USER,
        >>>     company_id=company.id
        >>> )
        >>> db.add(user)
        >>> db.commit()
        >>>
        >>> # Query user
        >>> user = db.query(User).filter(User.email == "john@example.com").first()
        >>> print(f"User: {user.full_name}, Role: {user.role}")
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "users"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the user"
    )

    # ========================================
    # Authentication & Identity Fields
    # ========================================
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's email address (unique identifier)"
    )

    google_id = Column(
        String(255),
        unique=True,
        nullable=True,
        comment="Google account ID for SSO authentication"
    )

    # ========================================
    # Profile Fields
    # ========================================
    full_name = Column(
        String(255),
        nullable=False,
        comment="User's full name"
    )

    profile_picture_url = Column(
        String(500),
        nullable=True,
        comment="URL to user's profile picture from Google"
    )

    # ========================================
    # Role & Permissions
    # ========================================
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER,
        index=True,
        comment="User's role (super_admin, admin, or user)"
    )

    # ========================================
    # Company Relationship
    # ========================================
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,  # NULL for super_admin users
        index=True,
        comment="Reference to the company this user belongs to"
    )

    # ========================================
    # Permissions
    # ========================================
    can_add_devices = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Permission flag - whether user can add new devices"
    )

    # ========================================
    # Account Status
    # ========================================
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account status - whether the account is active"
    )

    # ========================================
    # Timestamps
    # ========================================
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the account was created"
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Timestamp when the account was last updated"
    )

    last_login = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of the user's last login"
    )

    # ========================================
    # Relationships
    # ========================================

    # Many-to-One: User belongs to one Company
    company = relationship(
        "Company",
        back_populates="users",
        lazy="joined"  # Eager load company data when querying users
    )

    # One-to-Many: User can have multiple Devices
    devices = relationship(
        "Device",
        back_populates="user",
        cascade="all, delete-orphan",  # Delete devices when user is deleted
        lazy="select"  # Lazy load devices (only when accessed)
    )

    # One-to-One: User has one Google Drive Token
    # TODO: Uncomment when GoogleDriveToken model is implemented
    # google_drive_token = relationship(
    #     "GoogleDriveToken",
    #     back_populates="user",
    #     uselist=False,  # One-to-One relationship
    #     cascade="all, delete-orphan",
    #     lazy="select"
    # )

    # One-to-Many: User can send multiple Invitations
    invitations_sent = relationship(
        "Invitation",
        back_populates="invited_by_user",
        foreign_keys="[Invitation.invited_by]",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # One-to-Many: User can have multiple Audit Logs
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # ========================================
    # Model Methods
    # ========================================

    def is_super_admin(self) -> bool:
        """
        Check if user is a super admin.

        Returns:
            bool: True if user is super admin, False otherwise
        """
        return self.role == UserRole.SUPER_ADMIN

    def is_admin(self) -> bool:
        """
        Check if user is an admin (company level).

        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == UserRole.ADMIN

    def is_regular_user(self) -> bool:
        """
        Check if user is a regular user.

        Returns:
            bool: True if user is regular user, False otherwise
        """
        return self.role == UserRole.USER

    def can_manage_company(self, company_id: uuid.UUID) -> bool:
        """
        Check if user can manage the specified company.

        Super admins can manage all companies.
        Admins can only manage their own company.
        Regular users cannot manage companies.

        Args:
            company_id: UUID of the company to check

        Returns:
            bool: True if user can manage the company, False otherwise
        """
        if self.is_super_admin():
            return True
        if self.is_admin() and self.company_id == company_id:
            return True
        return False

    def can_manage_user(self, target_user: 'User') -> bool:
        """
        Check if user can manage the specified target user.

        Super admins can manage all users.
        Admins can manage users in their company (except other admins).
        Regular users cannot manage other users.

        Args:
            target_user: User object to check management rights for

        Returns:
            bool: True if user can manage the target user, False otherwise
        """
        if self.is_super_admin():
            return True
        if self.is_admin() and target_user.company_id == self.company_id:
            # Admins cannot manage other admins
            if target_user.is_admin() or target_user.is_super_admin():
                return False
            return True
        return False

    def update_last_login(self):
        """
        Update the last_login timestamp to current time.

        This method should be called whenever the user successfully logs in.
        """
        self.last_login = datetime.now(timezone.utc)

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the User object.

        Returns:
            str: String representation showing key user information
        """
        return (
            f"<User(id={self.id}, email='{self.email}', "
            f"role={self.role.value}, active={self.is_active})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: User's full name and email
        """
        return f"{self.full_name} ({self.email})"
