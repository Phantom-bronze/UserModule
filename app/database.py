"""
Database Module
===============

This module handles database connection, session management, and base model configuration.
It uses SQLAlchemy ORM for database operations with PostgreSQL.

The module provides:
- Database engine creation and configuration
- Session factory for database transactions
- Base model class for all database models
- Database initialization and table creation
- Dependency injection for FastAPI routes

Usage in API routes:
    from app.database import get_db

    @router.get("/users")
    def get_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.config import settings

# ============================================================
# Logging Configuration
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# Database Engine Configuration
# ============================================================

"""
Create SQLAlchemy engine with connection pooling.

Engine Configuration:
- poolclass: QueuePool for connection pooling
- pool_size: Number of connections to maintain in pool (from settings)
- max_overflow: Maximum additional connections beyond pool_size
- pool_timeout: Seconds to wait before giving up on getting a connection
- pool_recycle: Recycle connections after this many seconds (prevents stale connections)
- pool_pre_ping: Enable connection health checks before using
- echo: Log all SQL statements (useful for debugging, disabled in production)

Connection pooling improves performance by reusing database connections
instead of creating new ones for each request.
"""
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.DEBUG,  # Log SQL statements in debug mode
)


# ============================================================
# Session Factory Configuration
# ============================================================

"""
Create session factory for database transactions.

SessionLocal is a factory that creates new Session objects.
Each Session represents a database transaction and should be:
1. Created for each request
2. Used for all database operations in that request
3. Closed after the request is completed

Configuration:
- autocommit=False: Require explicit commit() calls for transactions
- autoflush=False: Require explicit flush() calls to send changes to DB
- bind=engine: Bind this session factory to our database engine
"""
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# Base Model Class
# ============================================================

"""
Base class for all SQLAlchemy models.

All database models should inherit from this Base class.
It provides:
- Automatic table name generation from class name
- Common metadata for all models
- Table creation and migration support

Example:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        email = Column(String, unique=True)
"""
Base = declarative_base()


# ============================================================
# Database Event Listeners
# ============================================================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Event listener for database connections.

    This function is called every time a new database connection is created.
    It can be used to set database-specific configuration options.

    For PostgreSQL, we can set:
    - Statement timeout to prevent long-running queries
    - Timezone settings
    - Other session-level parameters

    Args:
        dbapi_conn: The raw database connection
        connection_record: SQLAlchemy connection record
    """
    # For PostgreSQL, we can set statement timeout
    cursor = dbapi_conn.cursor()
    try:
        # Set statement timeout to 30 seconds to prevent hanging queries
        cursor.execute("SET statement_timeout = '30s'")
        cursor.close()
    except Exception as e:
        logger.warning(f"Failed to set statement timeout: {e}")


# ============================================================
# Database Session Dependency
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    This function creates a new database session for each request
    and ensures it's properly closed after the request is completed,
    even if an exception occurs.

    The session is yielded to the route handler, which can use it
    for database operations. After the route handler completes,
    the session is automatically closed.

    Usage in API routes:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

    Yields:
        Session: SQLAlchemy database session

    Example:
        >>> from fastapi import Depends
        >>> from app.database import get_db
        >>>
        >>> @app.get("/users")
        >>> def read_users(db: Session = Depends(get_db)):
        >>>     return db.query(User).all()
    """
    db = SessionLocal()
    try:
        # Yield the session to the route handler
        yield db
        # If no exception occurred, commit the transaction
        db.commit()
    except Exception as e:
        # If an exception occurred, rollback the transaction
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        # Always close the session, even if an exception occurred
        db.close()


# ============================================================
# Database Initialization
# ============================================================

def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function creates all tables defined by models that inherit
    from the Base class. It should be called once when the application
    starts or during deployment.

    Note: In production, use Alembic migrations instead of this function
    to manage database schema changes safely.

    Example:
        >>> from app.database import init_db
        >>> init_db()
        >>> print("Database initialized successfully!")

    Raises:
        Exception: If table creation fails
    """
    try:
        logger.info("Initializing database...")

        # Import all models here to ensure they are registered with Base
        # This is necessary for Base.metadata.create_all() to work
        from app.models import user, company, invitation, device  # noqa: F401

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This function deletes all data from the database!
    Use only for testing or development purposes.

    In production, use Alembic migrations to manage schema changes.

    Example:
        >>> from app.database import drop_db
        >>> drop_db()
        >>> print("All tables dropped!")

    Raises:
        Exception: If table deletion fails
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All tables dropped!")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


# ============================================================
# Database Health Check
# ============================================================

def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    This function attempts to execute a simple query to verify
    that the database is accessible and responsive.

    Returns:
        bool: True if database is accessible, False otherwise

    Example:
        >>> from app.database import check_db_connection
        >>> if check_db_connection():
        >>>     print("Database is healthy!")
        >>> else:
        >>>     print("Database connection failed!")
    """
    try:
        # Create a new session
        db = SessionLocal()

        # Execute a simple query to test the connection
        db.execute(text("SELECT 1"))

        # Close the session
        db.close()

        logger.info("Database connection is healthy")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


# ============================================================
# Transaction Context Manager
# ============================================================

class DatabaseTransaction:
    """
    Context manager for database transactions.

    This class provides a convenient way to handle database transactions
    with automatic commit on success and rollback on failure.

    Usage:
        with DatabaseTransaction() as db:
            user = User(email="test@example.com")
            db.add(user)
            # Transaction is automatically committed when exiting the context

    If an exception occurs within the context, the transaction is
    automatically rolled back.
    """

    def __init__(self):
        """Initialize the transaction context manager."""
        self.db: Session = None

    def __enter__(self) -> Session:
        """
        Enter the transaction context.

        Returns:
            Session: Database session for the transaction
        """
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        try:
            if exc_type is None:
                # No exception, commit the transaction
                self.db.commit()
                logger.debug("Transaction committed successfully")
            else:
                # Exception occurred, rollback the transaction
                self.db.rollback()
                logger.error(f"Transaction rolled back due to error: {exc_val}")
        finally:
            # Always close the session
            self.db.close()


# ============================================================
# Export commonly used objects
# ============================================================

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "init_db",
    "drop_db",
    "check_db_connection",
    "DatabaseTransaction",
]
