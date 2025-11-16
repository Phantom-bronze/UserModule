"""
Company Model
=============

This module defines the Company model which represents organizations/companies
in the multi-tenant system.

Each company:
- Has one or more admin users who manage it
- Can have multiple regular users
- Has its own Google Cloud credentials for Drive integration
- Has limits on number of users and devices
- Operates independently from other companies (data isolation)

The super admin creates companies and invites the first admin.
The admin then manages users and devices within their company.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Company(Base):
    """
    Company Model Class

    Represents an organization/company in the multi-tenant system.
    Each company operates as an independent entity with its own users,
    devices, content, and settings.

    Attributes:
        id (UUID): Unique identifier for the company (Primary Key)
        name (str): Company name (required)
        subdomain (str): Unique subdomain for the company (optional)
        logo_url (str): URL to company logo
        is_active (bool): Company status - whether the company is active
        max_users (int): Maximum number of users allowed in this company
        max_devices (int): Maximum number of devices allowed in this company
        created_at (datetime): Timestamp when the company was created
        updated_at (datetime): Timestamp when the company was last updated

    Relationships:
        users: List of users belonging to this company (One-to-Many with User)
        devices: List of devices belonging to this company (One-to-Many with Device)
        invitations: Invitations sent for this company (One-to-Many with Invitation)

    Database Table: companies

    Business Rules:
        - Each company must have at least one admin user
        - Company can have multiple regular users based on max_users limit
        - Company can have multiple devices based on max_devices limit
        - Only super admin can create, modify, or deactivate companies
        - Deactivating a company deactivates all its users and devices

    Example:
        >>> # Create a new company
        >>> company = Company(
        >>>     name="Acme Corporation",
        >>>     subdomain="acme",
        >>>     max_users=50,
        >>>     max_devices=100
        >>> )
        >>> db.add(company)
        >>> db.commit()
        >>>
        >>> # Query company with user count
        >>> company = db.query(Company).filter(Company.subdomain == "acme").first()
        >>> print(f"Company: {company.name}, Users: {len(company.users)}")
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "companies"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the company"
    )

    # ========================================
    # Company Information
    # ========================================
    name = Column(
        String(255),
        nullable=False,
        comment="Company name"
    )

    subdomain = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="Unique subdomain for the company (e.g., 'acme' for acme.yourdomain.com)"
    )

    logo_url = Column(
        String(500),
        nullable=True,
        comment="URL to company logo"
    )

    # ========================================
    # Company Status
    # ========================================
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Company status - whether the company is active"
    )

    # ========================================
    # Company Limits
    # ========================================
    max_users = Column(
        Integer,
        default=10,
        nullable=False,
        comment="Maximum number of users allowed in this company"
    )

    max_devices = Column(
        Integer,
        default=5,
        nullable=False,
        comment="Maximum number of devices allowed in this company"
    )

    # ========================================
    # Timestamps
    # ========================================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when the company was created"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when the company was last updated"
    )

    # ========================================
    # Relationships
    # ========================================

    # One-to-Many: Company has multiple Users
    users = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan",  # Delete users when company is deleted
        lazy="select"
    )

    # One-to-Many: Company has multiple Devices
    devices = relationship(
        "Device",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # One-to-One: Company has one Google Credential
    # TODO: Uncomment when GoogleCredential model is implemented
    # google_credential = relationship(
    #     "GoogleCredential",
    #     back_populates="company",
    #     uselist=False,  # One-to-One relationship
    #     cascade="all, delete-orphan",
    #     lazy="select"
    # )

    # One-to-Many: Company has multiple Invitations
    invitations = relationship(
        "Invitation",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # ========================================
    # Model Methods
    # ========================================

    def get_active_users_count(self, db_session) -> int:
        """
        Get the count of active users in this company.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            int: Number of active users in the company
        """
        from app.models.user import User
        return db_session.query(User).filter(
            User.company_id == self.id,
            User.is_active == True
        ).count()

    def get_devices_count(self, db_session) -> int:
        """
        Get the count of devices in this company.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            int: Number of devices in the company
        """
        from app.models.device import Device
        return db_session.query(Device).filter(
            Device.company_id == self.id
        ).count()

    def can_add_user(self, db_session) -> bool:
        """
        Check if the company can add more users based on max_users limit.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            bool: True if company can add more users, False otherwise
        """
        current_users = self.get_active_users_count(db_session)
        return current_users < self.max_users

    def can_add_device(self, db_session) -> bool:
        """
        Check if the company can add more devices based on max_devices limit.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            bool: True if company can add more devices, False otherwise
        """
        current_devices = self.get_devices_count(db_session)
        return current_devices < self.max_devices

    def get_admins(self, db_session) -> list:
        """
        Get all admin users for this company.

        Args:
            db_session: SQLAlchemy database session

        Returns:
            list: List of admin User objects
        """
        from app.models.user import User, UserRole
        return db_session.query(User).filter(
            User.company_id == self.id,
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).all()

    def deactivate(self, db_session):
        """
        Deactivate the company and all its users and devices.

        This method sets the company and all associated users/devices
        to inactive status. It does not delete any data.

        Args:
            db_session: SQLAlchemy database session
        """
        from app.models.user import User
        from app.models.device import Device

        # Deactivate the company
        self.is_active = False

        # Deactivate all users in the company
        db_session.query(User).filter(
            User.company_id == self.id
        ).update({"is_active": False})

        # Deactivate all devices in the company (mark as offline)
        db_session.query(Device).filter(
            Device.company_id == self.id
        ).update({"is_online": False})

        db_session.commit()

    def activate(self, db_session):
        """
        Activate the company (but not users - they must be activated individually).

        Args:
            db_session: SQLAlchemy database session
        """
        self.is_active = True
        db_session.commit()

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the Company object.

        Returns:
            str: String representation showing key company information
        """
        return (
            f"<Company(id={self.id}, name='{self.name}', "
            f"subdomain='{self.subdomain}', active={self.is_active})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Company name
        """
        return self.name
