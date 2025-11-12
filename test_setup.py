"""
Setup Verification Script
=========================

Run this script to verify your Simple Digital Signage backend setup.
It checks:
- Python dependencies
- Database connection
- Encryption configuration
- Email configuration (optional)
- Environment variables
"""

import sys
from typing import Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_test(name: str, passed: bool, message: str = ""):
    """Print test result."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if message:
        print(f"     {YELLOW}→ {message}{RESET}")


def test_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor}.{version.micro} (need 3.8+)"


def test_dependencies() -> Tuple[bool, str]:
    """Check if required packages are installed."""
    required = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'pydantic',
        'jose',
        'cryptography'
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, f"All {len(required)} required packages installed"


def test_environment_variables() -> Tuple[bool, str]:
    """Check if .env file exists and has required variables."""
    try:
        from app.config import settings

        required_vars = {
            'DATABASE_URL': settings.DATABASE_URL,
            'SECRET_KEY': settings.SECRET_KEY,
            'ENCRYPTION_KEY': settings.ENCRYPTION_KEY,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
            'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET
        }

        missing = []
        defaults = []

        for var, value in required_vars.items():
            if not value:
                missing.append(var)
            elif 'change-this' in value.lower() or 'your-' in value.lower():
                defaults.append(var)

        if missing:
            return False, f"Missing: {', '.join(missing)}"
        if defaults:
            return False, f"Using defaults: {', '.join(defaults)}"

        return True, "All required environment variables configured"

    except Exception as e:
        return False, f"Error loading config: {str(e)}"


def test_database_connection() -> Tuple[bool, str]:
    """Check database connection."""
    try:
        from app.database import check_db_connection

        if check_db_connection():
            return True, "Database connection successful"
        return False, "Cannot connect to database"

    except Exception as e:
        return False, f"Error: {str(e)}"


def test_encryption() -> Tuple[bool, str]:
    """Test encryption functionality."""
    try:
        from app.utils.encryption import encrypt_data, decrypt_data

        test_data = "Test encryption data"
        encrypted = encrypt_data(test_data)
        decrypted = decrypt_data(encrypted)

        if decrypted == test_data:
            return True, "Encryption working correctly"
        return False, "Decryption mismatch"

    except Exception as e:
        return False, f"Error: {str(e)}"


def test_database_tables() -> Tuple[bool, str]:
    """Check if database tables exist."""
    try:
        from app.database import engine
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'users',
            'companies',
            'devices',
            'invitations',
            'google_credentials',
            'google_drive_tokens',
            'audit_logs'
        ]

        missing = [t for t in expected_tables if t not in tables]

        if missing:
            return False, f"Missing tables: {', '.join(missing)} (run the app once to create)"

        return True, f"All {len(expected_tables)} tables exist"

    except Exception as e:
        return False, f"Error: {str(e)}"


def test_email_config() -> Tuple[bool, str]:
    """Check email configuration (non-critical)."""
    try:
        from app.config import settings

        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            return False, "SMTP credentials not configured (optional)"

        return True, f"Email configured ({settings.SMTP_HOST})"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Run all setup verification tests."""
    print_header("Simple Digital Signage - Setup Verification")

    print(f"{BLUE}Testing your setup...{RESET}\n")

    # Critical tests
    print(f"\n{BLUE}Critical Checks:{RESET}")

    passed, message = test_python_version()
    print_test("Python Version", passed, message)

    passed, message = test_dependencies()
    print_test("Python Dependencies", passed, message)

    passed, message = test_environment_variables()
    print_test("Environment Variables", passed, message)

    passed, message = test_database_connection()
    print_test("Database Connection", passed, message)

    passed, message = test_encryption()
    print_test("Encryption System", passed, message)

    # Optional tests
    print(f"\n{BLUE}Optional Checks:{RESET}")

    passed, message = test_database_tables()
    print_test("Database Tables", passed, message)

    passed, message = test_email_config()
    print_test("Email Configuration", passed, message)

    # Summary
    print_header("Summary")

    print(f"""
{GREEN}Next Steps:{RESET}

1. If all critical checks passed:
   {YELLOW}→{RESET} Run: python main.py
   {YELLOW}→{RESET} Open: http://localhost:8000/api/docs

2. If database tables are missing:
   {YELLOW}→{RESET} Start the app once to auto-create tables
   {YELLOW}→{RESET} Or run migrations if using Alembic

3. For first login:
   {YELLOW}→{RESET} Visit: http://localhost:8000/api/v1/auth/google/login
   {YELLOW}→{RESET} First user becomes Super Admin automatically

4. Check documentation:
   {YELLOW}→{RESET} Quick Start: QUICK_START.md
   {YELLOW}→{RESET} Full Docs: README.md
   {YELLOW}→{RESET} Database Schema: DATABASE_SCHEMA.md

{GREEN}Happy coding! 🚀{RESET}
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
