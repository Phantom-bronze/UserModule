"""
Configuration Module
====================

This module handles all application configuration settings loaded from environment variables.
It uses Pydantic Settings for validation and type safety.

The configuration is loaded from:
1. Environment variables
2. .env file (if present)
3. Default values (for development)

All sensitive information (passwords, secret keys, API credentials) should be
stored in environment variables and NEVER committed to version control.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application Settings Class

    This class defines all configuration parameters for the application.
    All settings can be overridden by environment variables.

    Attributes:
        APP_ENV: Application environment (development, staging, production)
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        HOST: Server host address
        PORT: Server port number
        DATABASE_URL: PostgreSQL database connection URL
        SECRET_KEY: Secret key for JWT token generation
        ALGORITHM: JWT algorithm
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days
        GOOGLE_CLIENT_ID: Google OAuth client ID
        GOOGLE_CLIENT_SECRET: Google OAuth client secret
        GOOGLE_REDIRECT_URI: Google OAuth redirect URI
        CORS_ORIGINS: List of allowed CORS origins
        ... and many more (see .env.example for full list)
    """

    # ============================================================
    # Application Settings
    # ============================================================
    APP_ENV: str = Field(default="development", description="Application environment")
    APP_NAME: str = Field(default="Simple Digital Signage", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=True, description="Debug mode flag")

    # ============================================================
    # Server Configuration
    # ============================================================
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8000, description="Server port number")

    # ============================================================
    # Database Configuration
    # ============================================================
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/simple_digital_signage",
        description="PostgreSQL database connection URL"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Maximum overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Connection pool timeout in seconds")

    # ============================================================
    # Security & Authentication
    # ============================================================
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-this-in-production",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    INVITATION_TOKEN_EXPIRE_HOURS: int = Field(
        default=72,
        description="Invitation token expiration time in hours"
    )
    ENCRYPTION_KEY: str = Field(
        default="your-encryption-key-here-change-this-in-production",
        description="Encryption key for sensitive data"
    )

    # ============================================================
    # Google OAuth Configuration
    # ============================================================
    GOOGLE_CLIENT_ID: str = Field(
        default="",
        description="Google OAuth client ID"
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        default="",
        description="Google OAuth client secret"
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth redirect URI"
    )
    GOOGLE_SCOPES: str = Field(
        default="openid,email,profile,https://www.googleapis.com/auth/drive.readonly",
        description="Google OAuth scopes (comma-separated)"
    )

    # ============================================================
    # CORS Configuration
    # ============================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://localhost:8100",
        description="Allowed CORS origins (comma-separated)"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )

    # ============================================================
    # Email Configuration
    # ============================================================
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USE_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    SMTP_USERNAME: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    FROM_EMAIL: str = Field(
        default="noreply@simpledigitalsignage.com",
        description="From email address"
    )
    FROM_NAME: str = Field(
        default="Simple Digital Signage",
        description="From name for emails"
    )

    # ============================================================
    # Redis Configuration
    # ============================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for Celery"
    )

    # ============================================================
    # File Storage Configuration
    # ============================================================
    LOCAL_STORAGE_PATH: str = Field(
        default="./storage/content",
        description="Local storage path for content"
    )
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=500,
        description="Maximum file upload size in MB"
    )
    ALLOWED_IMAGE_EXTENSIONS: str = Field(
        default="jpg,jpeg,png,gif,webp",
        description="Allowed image file extensions"
    )
    ALLOWED_VIDEO_EXTENSIONS: str = Field(
        default="mp4,avi,mov,wmv,flv,webm",
        description="Allowed video file extensions"
    )

    # ============================================================
    # Application Limits
    # ============================================================
    DEFAULT_MAX_USERS_PER_COMPANY: int = Field(
        default=10,
        description="Default maximum users per company"
    )
    DEFAULT_MAX_DEVICES_PER_COMPANY: int = Field(
        default=5,
        description="Default maximum devices per company"
    )
    MAX_DEVICES_PER_USER: int = Field(
        default=10,
        description="Maximum devices per user"
    )

    # ============================================================
    # Logging Configuration
    # ============================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")
    LOG_FILE_PATH: str = Field(default="", description="Log file path")

    # ============================================================
    # Super Admin Configuration
    # ============================================================
    SUPER_ADMIN_EMAIL: str = Field(
        default="admin@simpledigitalsignage.com",
        description="Initial super admin email"
    )
    SUPER_ADMIN_NAME: str = Field(
        default="Super Administrator",
        description="Initial super admin name"
    )

    # ============================================================
    # WebSocket Configuration
    # ============================================================
    WS_PING_INTERVAL: int = Field(
        default=30,
        description="WebSocket ping interval in seconds"
    )
    WS_PING_TIMEOUT: int = Field(
        default=10,
        description="WebSocket ping timeout in seconds"
    )

    # ============================================================
    # Device Configuration
    # ============================================================
    DEVICE_CODE_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Device pairing code expiration in minutes"
    )
    DEVICE_OFFLINE_TIMEOUT_MINUTES: int = Field(
        default=5,
        description="Device offline timeout in minutes"
    )

    # ============================================================
    # API Rate Limiting
    # ============================================================
    ENABLE_RATE_LIMITING: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit per minute"
    )

    # ============================================================
    # Monitoring & Analytics
    # ============================================================
    ENABLE_MONITORING: bool = Field(
        default=False,
        description="Enable application monitoring"
    )
    SENTRY_DSN: str = Field(
        default="",
        description="Sentry DSN for error tracking"
    )

    # ============================================================
    # Feature Flags
    # ============================================================
    ENABLE_REMOTE_CONTROL: bool = Field(
        default=True,
        description="Enable device remote control"
    )
    ENABLE_AUTO_UPDATE: bool = Field(
        default=True,
        description="Enable content auto-update"
    )
    ENABLE_ANALYTICS: bool = Field(
        default=True,
        description="Enable analytics and reporting"
    )

    # ============================================================
    # Validators
    # ============================================================

    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v: str) -> List[str]:
        """
        Validate and parse CORS origins from comma-separated string to list.

        Args:
            v: Comma-separated string of origins

        Returns:
            List of origin URLs
        """
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @validator("GOOGLE_SCOPES")
    def validate_google_scopes(cls, v: str) -> List[str]:
        """
        Validate and parse Google OAuth scopes from comma-separated string to list.

        Args:
            v: Comma-separated string of scopes

        Returns:
            List of scope strings
        """
        return [scope.strip() for scope in v.split(",") if scope.strip()]

    @validator("ALLOWED_IMAGE_EXTENSIONS", "ALLOWED_VIDEO_EXTENSIONS")
    def validate_extensions(cls, v: str) -> List[str]:
        """
        Validate and parse file extensions from comma-separated string to list.

        Args:
            v: Comma-separated string of extensions

        Returns:
            List of extension strings
        """
        return [ext.strip().lower() for ext in v.split(",") if ext.strip()]

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """
        Validate database URL format.

        Args:
            v: Database URL string

        Returns:
            Validated database URL

        Raises:
            ValueError: If database URL is invalid
        """
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with 'postgresql://'")
        return v

    @validator("SECRET_KEY", "ENCRYPTION_KEY")
    def validate_secret_keys(cls, v: str) -> str:
        """
        Validate that secret keys are changed from default in production.

        Args:
            v: Secret key value

        Returns:
            Validated secret key

        Raises:
            ValueError: If using default keys in production
        """
        if os.getenv("APP_ENV") == "production":
            if "change-this" in v.lower() or "your-" in v.lower():
                raise ValueError(
                    "You must change default secret keys in production! "
                    "Generate secure keys using: openssl rand -hex 32"
                )
        return v

    class Config:
        """
        Pydantic configuration class.

        Attributes:
            env_file: Path to .env file
            case_sensitive: Whether environment variable names are case-sensitive
        """
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.

    This function uses LRU cache to ensure settings are loaded only once
    and reused across the application. This improves performance and ensures
    consistency.

    Returns:
        Settings: Application settings instance

    Example:
        >>> from app.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.APP_NAME)
        'Simple Digital Signage'
    """
    return Settings()


# ============================================================
# Export settings instance for easy import
# ============================================================
settings = get_settings()
