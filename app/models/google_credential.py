"""
Google Credential Model
=======================

This module defines the GoogleCredential model for storing Google Cloud credentials
for each company.

Admin users can add Google Cloud credentials (OAuth client credentials) for their company.
These credentials are used to:
1. Authenticate users with Google SSO
2. Access Google Drive API to fetch content
3. Manage Google API quotas and limits per company

Security:
- Credentials are encrypted at rest using the ENCRYPTION_KEY
- Only admin users of the company can view/modify credentials
- Credentials are validated before storage
- Failed validation logs are maintained for audit purposes
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class GoogleCredential(Base):
    """
    Google Credential Model Class

    Stores Google Cloud OAuth credentials for companies to enable
    Google Drive integration and SSO authentication.

    Each company can have one set of Google Cloud credentials which
    enables all users in that company to:
    - Authenticate via Google SSO
    - Connect their Google Drive accounts
    - Import content from Google Drive

    Attributes:
        id (UUID): Unique identifier for the credential (Primary Key)
        company_id (UUID): Company these credentials belong to (Foreign Key, Unique)
        client_id (str): Google OAuth client ID (required)
        client_secret (str): Google OAuth client secret (encrypted, required)
        project_id (str): Google Cloud project ID
        service_account_email (str): Service account email (if using service account)
        credentials_json (str): Full credentials JSON (encrypted)
        is_valid (bool): Whether credentials are currently valid
        created_by (UUID): Admin who added the credentials (Foreign Key)
        created_at (datetime): Timestamp when credentials were added
        updated_at (datetime): Timestamp when credentials were last updated
        last_validated (datetime): Timestamp of last successful validation

    Relationships:
        company: The company these credentials belong to (One-to-One with Company)
        creator: The admin user who created these credentials (Many-to-One with User)

    Database Table: google_credentials

    Business Rules:
        - Each company can have only ONE set of Google Cloud credentials
        - Only admin users can add/update credentials
        - Credentials must be validated before storage
        - Invalid credentials are rejected with clear error messages
        - Credentials are encrypted using AES-256 encryption

    Security Considerations:
        - client_secret and credentials_json are encrypted at rest
        - Encryption key is stored in environment variables (ENCRYPTION_KEY)
        - Credentials are never logged or displayed in plain text
        - Failed validation attempts are logged for security audit

    Example:
        >>> # Add Google credentials for a company
        >>> from app.utils.encryption import encrypt_data
        >>>
        >>> credentials = GoogleCredential(
        >>>     company_id=company.id,
        >>>     client_id="123456789.apps.googleusercontent.com",
        >>>     client_secret=encrypt_data("your-client-secret"),
        >>>     project_id="my-project-id",
        >>>     credentials_json=encrypt_data(json.dumps(creds_dict)),
        >>>     created_by=admin.id
        >>> )
        >>> db.add(credentials)
        >>> db.commit()
    """

    # ========================================
    # Table Configuration
    # ========================================
    __tablename__ = "google_credentials"

    # ========================================
    # Primary Key
    # ========================================
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the credential"
    )

    # ========================================
    # Company Relationship (One-to-One)
    # ========================================
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        unique=True,  # Each company can have only one set of credentials
        nullable=False,
        index=True,
        comment="Company these credentials belong to"
    )

    # ========================================
    # Google OAuth Credentials
    # ========================================
    client_id = Column(
        String(500),
        nullable=False,
        comment="Google OAuth client ID"
    )

    client_secret = Column(
        String(500),
        nullable=False,
        comment="Google OAuth client secret (encrypted)"
    )

    project_id = Column(
        String(255),
        nullable=True,
        comment="Google Cloud project ID"
    )

    service_account_email = Column(
        String(255),
        nullable=True,
        comment="Service account email (if using service account)"
    )

    # ========================================
    # Full Credentials JSON
    # ========================================
    credentials_json = Column(
        Text,
        nullable=False,
        comment="Full credentials JSON (encrypted)"
    )

    # ========================================
    # Validation Status
    # ========================================
    is_valid = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether credentials are currently valid"
    )

    # ========================================
    # Created By
    # ========================================
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Admin who added the credentials"
    )

    # ========================================
    # Timestamps
    # ========================================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Timestamp when credentials were added"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Timestamp when credentials were last updated"
    )

    last_validated = Column(
        DateTime,
        nullable=True,
        comment="Timestamp of last successful validation"
    )

    # ========================================
    # Relationships
    # ========================================

    # One-to-One: GoogleCredential belongs to one Company
    company = relationship(
        "Company",
        back_populates="google_credential",
        lazy="joined"
    )

    # Many-to-One: GoogleCredential created by one User (admin)
    creator = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="select"
    )

    # ========================================
    # Model Methods
    # ========================================

    def mark_as_valid(self):
        """
        Mark credentials as valid and update last_validated timestamp.

        This should be called after successful validation of credentials
        with Google API.
        """
        self.is_valid = True
        self.last_validated = datetime.utcnow()

    def mark_as_invalid(self):
        """
        Mark credentials as invalid.

        This should be called when credentials fail validation or
        Google API returns authentication errors.
        """
        self.is_valid = False

    def needs_revalidation(self, hours: int = 24) -> bool:
        """
        Check if credentials need revalidation.

        Credentials should be periodically validated to ensure they
        are still working with Google API.

        Args:
            hours: Number of hours since last validation to trigger revalidation

        Returns:
            bool: True if credentials need revalidation, False otherwise
        """
        if not self.last_validated:
            return True

        time_since_validation = datetime.utcnow() - self.last_validated
        return time_since_validation.total_seconds() > (hours * 3600)

    def get_decrypted_client_secret(self) -> str:
        """
        Get decrypted client secret.

        WARNING: This method returns sensitive data. Use with caution
        and never log or display the result.

        Returns:
            str: Decrypted client secret

        Example:
            >>> from app.utils.encryption import decrypt_data
            >>> secret = decrypt_data(credentials.client_secret)
        """
        from app.utils.encryption import decrypt_data
        return decrypt_data(self.client_secret)

    def get_decrypted_credentials_json(self) -> str:
        """
        Get decrypted credentials JSON.

        WARNING: This method returns sensitive data. Use with caution
        and never log or display the result.

        Returns:
            str: Decrypted credentials JSON

        Example:
            >>> from app.utils.encryption import decrypt_data
            >>> import json
            >>> creds_dict = json.loads(decrypt_data(credentials.credentials_json))
        """
        from app.utils.encryption import decrypt_data
        return decrypt_data(self.credentials_json)

    @staticmethod
    def create_from_json(company_id: uuid.UUID, credentials_dict: dict,
                        created_by: uuid.UUID) -> 'GoogleCredential':
        """
        Create GoogleCredential instance from credentials dictionary.

        This static method handles encryption of sensitive data and
        creates a properly formatted GoogleCredential instance.

        Args:
            company_id: UUID of the company
            credentials_dict: Dictionary containing Google Cloud credentials
            created_by: UUID of the admin creating the credentials

        Returns:
            GoogleCredential: New GoogleCredential instance (not yet saved to DB)

        Raises:
            ValueError: If credentials_dict is missing required fields

        Example:
            >>> creds_dict = {
            >>>     "client_id": "123.apps.googleusercontent.com",
            >>>     "client_secret": "secret",
            >>>     "project_id": "my-project"
            >>> }
            >>> credential = GoogleCredential.create_from_json(
            >>>     company.id, creds_dict, admin.id
            >>> )
            >>> db.add(credential)
            >>> db.commit()
        """
        import json
        from app.utils.encryption import encrypt_data

        # Validate required fields
        required_fields = ["client_id", "client_secret"]
        for field in required_fields:
            if field not in credentials_dict:
                raise ValueError(f"Missing required field: {field}")

        # Extract fields
        client_id = credentials_dict.get("client_id")
        client_secret = credentials_dict.get("client_secret")
        project_id = credentials_dict.get("project_id")
        service_account_email = credentials_dict.get("client_email")

        # Encrypt sensitive data
        encrypted_secret = encrypt_data(client_secret)
        encrypted_json = encrypt_data(json.dumps(credentials_dict))

        # Create instance
        return GoogleCredential(
            company_id=company_id,
            client_id=client_id,
            client_secret=encrypted_secret,
            project_id=project_id,
            service_account_email=service_account_email,
            credentials_json=encrypted_json,
            created_by=created_by
        )

    # ========================================
    # String Representation
    # ========================================

    def __repr__(self) -> str:
        """
        String representation of the GoogleCredential object.

        Note: Does not include sensitive data.

        Returns:
            str: String representation showing key credential information
        """
        return (
            f"<GoogleCredential(id={self.id}, company_id={self.company_id}, "
            f"project_id='{self.project_id}', valid={self.is_valid})>"
        )

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            str: Project ID and validation status
        """
        status = "Valid" if self.is_valid else "Invalid"
        return f"Google Credentials for {self.project_id} ({status})"
