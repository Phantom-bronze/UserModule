"""
Audit Log Model
===============

This module defines the AuditLog model for tracking all important actions
in the system for security, compliance, and debugging purposes.

The audit log records:
- Who performed the action (user)
- What action was performed (create, update, delete, etc.)
- When it was performed (timestamp)
- What resource was affected (user, company, device, etc.)
- Additional context (IP address, user agent, details)

This provides a complete audit trail for:
- Security investigations
- Compliance requirements
- Debugging issues
- User activity monitoring
- Admin action tracking
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class AuditLog(Base):
    """
    Audit Log Model Class

    Records all important actions performed in the system for audit trail,
    security monitoring, and compliance purposes.

    Every significant action should be logged including:
    - User creation, updates, deletion
    - Company creation, updates, deactivation
    - Device linking, unlinking, status changes
    - Content uploads, deletions
    - Playlist creation, updates
    - Permission changes
    - Login/logout events
    - Google credentials updates
    - Invitation sent/accepted

    Attributes:
        id (UUID): Unique identifier for the log entry (Primary Key)
        user_id (UUID): User who performed the action (Foreign Key, nullable)
        action (str): Action performed (e.g., "user.created", "device.linked")
        resource_type (str): Type of resource affected (e.g., "user", "device")
        resource_id (UUID): ID of the resource affected
        details (dict): Additional context as JSON (old/new values, etc.)
        ip_address (str): IP address of the user
        user_agent (str): Browser/app user agent string
        created_at (datetime): Timestamp when action was performed

    Relationships:
        user: The user who performed the action (Many-to-One with User)

    Database Table: audit_logs

    Action Naming Convention:
        Format: "{resource}.{operation}"
        Examples:
            - "user.created" - User account was created
            - "user.updated" - User account was updated
            - "user.deleted" - User account was deleted
            - "device.linked" - Device was linked to user
            - "company.created" - Company was created
            - "credentials.added" - Google credentials were added
            - "invitation.sent" - Invitation was sent
            - "auth.login" - User logged in
            - "auth.logout" - User logged out

    Security Considerations:
        - Logs are immutable (no updates or deletes)
        - Sensitive data (passwords, tokens) are never logged
        - Logs are retained for compliance requirements
        - Access to logs is restricted to super admins
        - Logs can be exported for external audit systems

    Example:
        >>> # Log a user creation action
        >>> audit_log = AuditLog.create_log(
        >>>     user_id=admin.id,
        >>>     action="user.created",
        >>>     resource_type="user",
        >>>     resource_id=new_user.id,
        >>>     details={
        >>>         "email": new_user.email,
        >>>         "role": new_user.role,
        >>>         "company_id": str(new_user.company_id)
        >>>     },
        >>>     ip_address=request.client.host,
        >>>     user_agent=request.headers.get("user-agent")
        >>> )
        >>> db.add(audit_log)
        >>> db.commit()
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "audit_logs"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the log entry"
    )

    # ========================================
    # User Who Performed Action
    # ========================================
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # NULL for system actions or deleted users
        index=True,
        comment="User who performed the action"
    )

    # ========================================
    # Action Information
    # ========================================
    action = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (e.g., 'user.created', 'device.linked')"
    )

    resource_type = Column(
        String(50),
        nullable=True,
        comment="Type of resource affected (e.g., 'user', 'device', 'company')"
    )

    resource_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of the resource affected"
    )

    # ========================================
    # Additional Context (JSON)
    # ========================================
    details = Column(
        JSONB,
        nullable=True,
        comment="Additional context as JSON (old/new values, parameters, etc.)"
    )

    # ========================================
    # Request Information
    # ========================================
    ip_address = Column(
        String(45),  # IPv6 addresses can be up to 45 characters
        nullable=True,
        comment="IP address of the user/client"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="Browser/app user agent string"
    )

    # ========================================
    # Timestamp
    # ========================================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Timestamp when the action was performed"
    )

    # ========================================
    # Relationships
    # ========================================

    # Many-to-One: AuditLog belongs to one User
    user = relationship(
        "User",
        back_populates="audit_logs",
        lazy="joined"
    )

    # ========================================
    # Indexes for Performance
    # ========================================
    __table_args__ = (
        # Composite index for common queries
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created_at_desc', created_at.desc()),
    )

    # ========================================
    # Model Methods
    # ========================================

    @staticmethod
    def create_log(
        action: str,
        user_id: uuid.UUID = None,
        resource_type: str = None,
        resource_id: uuid.UUID = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> 'AuditLog':
        """
        Create a new audit log entry.

        This static method provides a convenient way to create audit logs
        with all necessary information.

        Args:
            action: Action performed (e.g., "user.created")
            user_id: User who performed the action (optional for system actions)
            resource_type: Type of resource affected (optional)
            resource_id: ID of the resource affected (optional)
            details: Additional context as dictionary (optional)
            ip_address: IP address of the user (optional)
            user_agent: Browser/app user agent (optional)

        Returns:
            AuditLog: New AuditLog instance (not yet saved to DB)

        Example:
            >>> log = AuditLog.create_log(
            >>>     action="user.login",
            >>>     user_id=user.id,
            >>>     ip_address="192.168.1.1",
            >>>     details={"method": "google_oauth"}
            >>> )
            >>> db.add(log)
            >>> db.commit()
        """
        return AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_user_action(
        user_id: uuid.UUID,
        action: str,
        resource_type: str = None,
        resource_id: uuid.UUID = None,
        details: dict = None,
        request = None
    ) -> 'AuditLog':
        """
        Create an audit log for a user action with request info.

        This is a convenience method that automatically extracts
        IP address and user agent from the request object.

        Args:
            user_id: User who performed the action
            action: Action performed
            resource_type: Type of resource affected (optional)
            resource_id: ID of the resource affected (optional)
            details: Additional context (optional)
            request: FastAPI Request object (optional)

        Returns:
            AuditLog: New AuditLog instance (not yet saved to DB)

        Example:
            >>> from fastapi import Request
            >>>
            >>> @app.post("/users")
            >>> def create_user(request: Request, db: Session = Depends(get_db)):
            >>>     # ... create user logic ...
            >>>     log = AuditLog.log_user_action(
            >>>         user_id=current_user.id,
            >>>         action="user.created",
            >>>         resource_type="user",
            >>>         resource_id=new_user.id,
            >>>         details={"email": new_user.email},
            >>>         request=request
            >>>     )
            >>>     db.add(log)
            >>>     db.commit()
        """
        ip_address = None
        user_agent = None

        if request:
            # Extract IP address
            if hasattr(request, 'client') and request.client:
                ip_address = request.client.host

            # Extract user agent
            if hasattr(request, 'headers'):
                user_agent = request.headers.get("user-agent")

        return AuditLog.create_log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_system_action(
        action: str,
        resource_type: str = None,
        resource_id: uuid.UUID = None,
        details: dict = None
    ) -> 'AuditLog':
        """
        Create an audit log for a system action (no user).

        System actions are automated processes that don't have a user
        context, such as:
        - Scheduled tasks
        - Background jobs
        - Automated cleanups
        - Health checks

        Args:
            action: Action performed
            resource_type: Type of resource affected (optional)
            resource_id: ID of the resource affected (optional)
            details: Additional context (optional)

        Returns:
            AuditLog: New AuditLog instance (not yet saved to DB)

        Example:
            >>> log = AuditLog.log_system_action(
            >>>     action="device.marked_offline",
            >>>     resource_type="device",
            >>>     resource_id=device.id,
            >>>     details={"reason": "no_heartbeat", "last_seen": str(device.last_seen)}
            >>> )
            >>> db.add(log)
            >>> db.commit()
        """
        return AuditLog.create_log(
            action=action,
            user_id=None,  # No user for system actions
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )

    def get_user_info(self) -> dict:
        """
        Get information about the user who performed the action.

        Returns:
            dict: User information or indication it was a system action

        Example:
            >>> user_info = log.get_user_info()
            >>> print(user_info)
            {'id': 'uuid', 'email': 'admin@example.com', 'name': 'Admin User'}
        """
        if not self.user:
            return {"type": "system", "name": "System"}

        return {
            "id": str(self.user.id),
            "email": self.user.email,
            "name": self.user.full_name,
            "role": self.user.role.value if hasattr(self.user.role, 'value') else self.user.role
        }

    def to_dict(self) -> dict:
        """
        Convert audit log to dictionary for API responses.

        Returns:
            dict: Audit log data as dictionary

        Example:
            >>> log_dict = log.to_dict()
            >>> return JSONResponse(content=log_dict)
        """
        return {
            "id": str(self.id),
            "user": self.get_user_info(),
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the AuditLog object.

        Returns:
            str: String representation showing key log information
        """
        user_info = f"user={self.user_id}" if self.user_id else "system"
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"{user_info}, created_at={self.created_at})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Action and timestamp
        """
        user_name = self.user.full_name if self.user else "System"
        return f"{user_name} performed {self.action} at {self.created_at}"


# ============================================================
# Common Audit Actions (Constants)
# ============================================================

class AuditAction:
    """
    Constants for common audit actions.

    Using constants helps maintain consistency across the application
    and makes it easier to search for specific actions.

    Usage:
        >>> from app.models.audit_log import AuditAction
        >>> log = AuditLog.create_log(
        >>>     action=AuditAction.USER_CREATED,
        >>>     user_id=admin.id
        >>> )
    """
    # Authentication actions
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"

    # User actions
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_ACTIVATED = "user.activated"
    USER_DEACTIVATED = "user.deactivated"
    USER_ROLE_CHANGED = "user.role_changed"
    USER_PERMISSION_CHANGED = "user.permission_changed"

    # Company actions
    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"
    COMPANY_DELETED = "company.deleted"
    COMPANY_ACTIVATED = "company.activated"
    COMPANY_DEACTIVATED = "company.deactivated"

    # Invitation actions
    INVITATION_SENT = "invitation.sent"
    INVITATION_ACCEPTED = "invitation.accepted"
    INVITATION_CANCELLED = "invitation.cancelled"
    INVITATION_EXPIRED = "invitation.expired"

    # Device actions
    DEVICE_CREATED = "device.created"
    DEVICE_LINKED = "device.linked"
    DEVICE_UNLINKED = "device.unlinked"
    DEVICE_UPDATED = "device.updated"
    DEVICE_DELETED = "device.deleted"
    DEVICE_ONLINE = "device.online"
    DEVICE_OFFLINE = "device.offline"

    # Google credentials actions
    CREDENTIALS_ADDED = "credentials.added"
    CREDENTIALS_UPDATED = "credentials.updated"
    CREDENTIALS_DELETED = "credentials.deleted"
    CREDENTIALS_VALIDATED = "credentials.validated"
    CREDENTIALS_INVALID = "credentials.invalid"

    # Google Drive actions
    DRIVE_CONNECTED = "drive.connected"
    DRIVE_DISCONNECTED = "drive.disconnected"
    DRIVE_TOKEN_REFRESHED = "drive.token_refreshed"

    # Content actions (for future use)
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_DELETED = "content.deleted"
    CONTENT_UPDATED = "content.updated"

    # Playlist actions (for future use)
    PLAYLIST_CREATED = "playlist.created"
    PLAYLIST_UPDATED = "playlist.updated"
    PLAYLIST_DELETED = "playlist.deleted"
    PLAYLIST_ASSIGNED = "playlist.assigned"
