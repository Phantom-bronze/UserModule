"""
Google Drive Token Model
========================

This module defines the GoogleDriveToken model for storing user-specific
Google Drive access and refresh tokens.

Each user can link their personal Google Drive account to import content.
The tokens stored here allow the system to:
1. Access user's Google Drive files (images and videos)
2. List files and folders in Drive
3. Download content to display on TVs
4. Refresh access tokens when they expire

Security:
- Tokens are encrypted at rest
- Each user has their own tokens (not shared)
- Tokens can be revoked by user at any time
- Automatic token refresh using refresh token
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.database import Base


class GoogleDriveToken(Base):
    """
    Google Drive Token Model Class

    Stores user-specific Google Drive OAuth tokens for accessing their
    Google Drive files to import content.

    Each user links their personal Google Drive account and grants permission
    to read their files. The access and refresh tokens are stored securely
    and used to fetch content from Drive.

    Attributes:
        id (UUID): Unique identifier for the token record (Primary Key)
        user_id (UUID): User who owns this token (Foreign Key, Unique)
        access_token (str): Google Drive access token (encrypted, required)
        refresh_token (str): Google Drive refresh token (encrypted, required)
        token_expiry (datetime): When the access token expires
        scope (str): OAuth scopes granted by user
        created_at (datetime): Timestamp when token was first created
        updated_at (datetime): Timestamp when token was last refreshed

    Relationships:
        user: The user who owns this token (One-to-One with User)

    Database Table: google_drive_tokens

    Token Lifecycle:
        1. User authorizes app to access their Google Drive
        2. App receives access_token and refresh_token from Google
        3. Tokens are encrypted and stored in database
        4. When access_token expires, use refresh_token to get new access_token
        5. User can revoke access anytime (deletes the token record)

    Security Considerations:
        - All tokens are encrypted using AES-256
        - Encryption key is stored in environment variables
        - Tokens are never logged or displayed in plain text
        - Failed token refresh triggers user re-authentication

    Example:
        >>> # Store user's Google Drive tokens
        >>> from app.utils.encryption import encrypt_data
        >>>
        >>> token = GoogleDriveToken(
        >>>     user_id=user.id,
        >>>     access_token=encrypt_data(access_token),
        >>>     refresh_token=encrypt_data(refresh_token),
        >>>     token_expiry=datetime.utcnow() + timedelta(hours=1),
        >>>     scope="https://www.googleapis.com/auth/drive.readonly"
        >>> )
        >>> db.add(token)
        >>> db.commit()
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "google_drive_tokens"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the token record"
    )

    # ========================================
    # User Relationship (One-to-One)
    # ========================================
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # Each user can have only one Google Drive token record
        nullable=False,
        index=True,
        comment="User who owns this token"
    )

    # ========================================
    # OAuth Tokens
    # ========================================
    access_token = Column(
        Text,
        nullable=False,
        comment="Google Drive access token (encrypted)"
    )

    refresh_token = Column(
        Text,
        nullable=False,
        comment="Google Drive refresh token (encrypted)"
    )

    # ========================================
    # Token Metadata
    # ========================================
    token_expiry = Column(
        DateTime,
        nullable=False,
        comment="When the access token expires"
    )

    scope = Column(
        Text,
        nullable=True,
        comment="OAuth scopes granted by user"
    )

    # ========================================
    # Timestamps
    # ========================================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when token was first created"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when token was last refreshed"
    )

    # ========================================
    # Relationships
    # ========================================

    # One-to-One: GoogleDriveToken belongs to one User
    user = relationship(
        "User",
        back_populates="google_drive_token",
        lazy="joined"
    )

    # ========================================
    # Model Methods
    # ========================================

    def is_expired(self) -> bool:
        """
        Check if the access token has expired.

        Returns:
            bool: True if token is expired, False otherwise
        """
        return datetime.utcnow() >= self.token_expiry

    def needs_refresh(self, buffer_minutes: int = 5) -> bool:
        """
        Check if the token needs to be refreshed.

        It's good practice to refresh tokens a few minutes before they
        actually expire to avoid authentication errors.

        Args:
            buffer_minutes: Refresh token this many minutes before expiry

        Returns:
            bool: True if token should be refreshed, False otherwise
        """
        refresh_threshold = self.token_expiry - timedelta(minutes=buffer_minutes)
        return datetime.utcnow() >= refresh_threshold

    def update_tokens(self, access_token: str, token_expiry: datetime,
                     refresh_token: str = None):
        """
        Update the stored tokens after refresh.

        Args:
            access_token: New access token (encrypted)
            token_expiry: New expiry datetime
            refresh_token: New refresh token (encrypted, optional)

        Note:
            Refresh token might not be returned by Google on every refresh.
            If not provided, keep the existing refresh token.
        """
        self.access_token = access_token
        self.token_expiry = token_expiry

        if refresh_token:
            self.refresh_token = refresh_token

        self.updated_at = datetime.utcnow()

    def get_decrypted_access_token(self) -> str:
        """
        Get decrypted access token.

        WARNING: This method returns sensitive data. Use with caution
        and never log or display the result.

        Returns:
            str: Decrypted access token

        Example:
            >>> from app.utils.encryption import decrypt_data
            >>> token = decrypt_data(drive_token.access_token)
        """
        from app.utils.encryption import decrypt_data
        return decrypt_data(self.access_token)

    def get_decrypted_refresh_token(self) -> str:
        """
        Get decrypted refresh token.

        WARNING: This method returns sensitive data. Use with caution
        and never log or display the result.

        Returns:
            str: Decrypted refresh token

        Example:
            >>> from app.utils.encryption import decrypt_data
            >>> token = decrypt_data(drive_token.refresh_token)
        """
        from app.utils.encryption import decrypt_data
        return decrypt_data(self.refresh_token)

    def time_until_expiry(self) -> timedelta:
        """
        Calculate time remaining until token expires.

        Returns:
            timedelta: Time remaining until expiration (can be negative if expired)
        """
        return self.token_expiry - datetime.utcnow()

    @staticmethod
    def create_from_google_response(user_id: uuid.UUID, token_response: dict) -> 'GoogleDriveToken':
        """
        Create GoogleDriveToken instance from Google OAuth response.

        This static method handles encryption of sensitive data and
        creates a properly formatted GoogleDriveToken instance.

        Args:
            user_id: UUID of the user
            token_response: Dictionary from Google OAuth token endpoint

        Returns:
            GoogleDriveToken: New GoogleDriveToken instance (not yet saved to DB)

        Raises:
            ValueError: If token_response is missing required fields

        Example:
            >>> token_response = {
            >>>     "access_token": "ya29.xxx",
            >>>     "refresh_token": "1//xxx",
            >>>     "expires_in": 3600,
            >>>     "scope": "https://www.googleapis.com/auth/drive.readonly"
            >>> }
            >>> drive_token = GoogleDriveToken.create_from_google_response(
            >>>     user.id, token_response
            >>> )
            >>> db.add(drive_token)
            >>> db.commit()
        """
        from app.utils.encryption import encrypt_data

        # Validate required fields
        if "access_token" not in token_response:
            raise ValueError("Missing access_token in token response")
        if "refresh_token" not in token_response:
            raise ValueError("Missing refresh_token in token response")

        # Extract fields
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 3600)  # Default 1 hour
        scope = token_response.get("scope", "")

        # Calculate expiry time
        token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)

        # Encrypt sensitive data
        encrypted_access = encrypt_data(access_token)
        encrypted_refresh = encrypt_data(refresh_token)

        # Create instance
        return GoogleDriveToken(
            user_id=user_id,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            token_expiry=token_expiry,
            scope=scope
        )

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the GoogleDriveToken object.

        Note: Does not include sensitive token data.

        Returns:
            str: String representation showing key information
        """
        expired = "Expired" if self.is_expired() else "Valid"
        return (
            f"<GoogleDriveToken(id={self.id}, user_id={self.user_id}, "
            f"status={expired}, expires_at={self.token_expiry})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Token status and expiry time
        """
        if self.is_expired():
            return "Google Drive Token (Expired)"
        else:
            time_left = self.time_until_expiry()
            hours = int(time_left.total_seconds() / 3600)
            return f"Google Drive Token (Valid, expires in {hours}h)"
