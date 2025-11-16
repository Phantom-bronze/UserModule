"""
Local Database Initialization Script
=====================================

This script initializes the database locally without Docker.
It creates all tables and optionally populates sample data.

Usage:
    python init_local_db.py                    # Just create tables
    python init_local_db.py --sample-data      # Create tables + sample data
    python init_local_db.py --reset            # Drop all tables and recreate
"""

import sys
import argparse
from datetime import datetime, timedelta
import secrets

# Add app to path
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from app.database import Base, get_db
from app.config import settings
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.device import Device
from app.models.invitation import Invitation, InvitationStatus
from app.models.google_credential import GoogleCredential
from app.models.google_drive_token import GoogleDriveToken
from app.models.audit_log import AuditLog
from app.utils.encryption import encrypt_data


def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def check_database_connection():
    """Check if database is accessible"""
    print("[*] Checking database connection...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[OK] Connected to PostgreSQL: {version}\n")
            return engine
    except Exception as e:
        print(f"[ERROR] Failed to connect to database!")
        print(f"   Error: {e}")
        print(f"\n[INFO] Make sure PostgreSQL is running and DATABASE_URL is correct:")
        print(f"   DATABASE_URL={settings.DATABASE_URL}\n")
        return None


def create_tables(engine, reset=False):
    """Create all database tables"""
    print_header("Creating Database Tables")

    if reset:
        print("[WARNING] Dropping all existing tables...")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("[ERROR] Cancelled.")
            return False

        print("[*] Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("[OK] All tables dropped.\n")

    print("[*] Creating tables...")
    Base.metadata.create_all(bind=engine)

    # List all created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("[OK] Tables created successfully:\n")
    for table in tables:
        print(f"   [OK] {table}")

    print(f"\n[*] Total tables: {len(tables)}")
    return True


def create_sample_data():
    """Create sample data for testing"""
    print_header("Creating Sample Data")

    from sqlalchemy.orm import Session
    engine = create_engine(settings.DATABASE_URL)
    db = Session(bind=engine)

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"[WARNING] Database already has {existing_users} users.")
            response = input("Do you want to add more sample data? (yes/no): ")
            if response.lower() != 'yes':
                print("[ERROR] Cancelled.")
                return

        print("[*] Creating sample users and companies...\n")

        # 1. Create Super Admin
        print("[1] Creating Super Admin...")
        super_admin = User(
            email="admin@example.com",
            google_id="super_admin_google_id",
            full_name="Super Administrator",
            profile_picture_url="https://via.placeholder.com/150",
            role=UserRole.SUPER_ADMIN,
            company_id=None,
            is_active=True,
            last_login=datetime.utcnow()
        )
        db.add(super_admin)
        db.flush()
        print(f"   [OK] Super Admin created: {super_admin.email}")

        # 2. Create Companies
        print("\n[2] Creating companies...")

        companies_data = [
            {
                "name": "Acme Corporation",
                "subdomain": "acme",
                "max_users": 50,
                "max_devices": 100
            },
            {
                "name": "TechStart Inc",
                "subdomain": "techstart",
                "max_users": 20,
                "max_devices": 30
            },
            {
                "name": "Global Retail",
                "subdomain": "globalretail",
                "max_users": 100,
                "max_devices": 200
            }
        ]

        companies = []
        for company_data in companies_data:
            company = Company(**company_data)
            db.add(company)
            db.flush()
            companies.append(company)
            print(f"   [OK] Company created: {company.name} ({company.subdomain})")

        # 3. Create Company Admins
        print("\n[3] Creating company admins...")

        admins_data = [
            {
                "email": "admin@acme.com",
                "google_id": "acme_admin_google_id",
                "full_name": "John Smith",
                "company": companies[0],
                "can_add_devices": True
            },
            {
                "email": "admin@techstart.com",
                "google_id": "techstart_admin_google_id",
                "full_name": "Sarah Johnson",
                "company": companies[1],
                "can_add_devices": True
            },
            {
                "email": "admin@globalretail.com",
                "google_id": "globalretail_admin_google_id",
                "full_name": "Michael Chen",
                "company": companies[2],
                "can_add_devices": True
            }
        ]

        admins = []
        for admin_data in admins_data:
            company = admin_data.pop('company')
            admin = User(
                **admin_data,
                role=UserRole.ADMIN,
                company_id=company.id,
                is_active=True,
                last_login=datetime.utcnow()
            )
            db.add(admin)
            db.flush()
            admins.append(admin)
            print(f"   [OK] Admin created: {admin.email} for {company.name}")

        # 4. Create Regular Users
        print("\n[4] Creating regular users...")

        users_data = [
            {
                "email": "user1@acme.com",
                "google_id": "user1_google_id",
                "full_name": "Alice Brown",
                "company": companies[0],
                "can_add_devices": True
            },
            {
                "email": "user2@acme.com",
                "google_id": "user2_google_id",
                "full_name": "Bob Wilson",
                "company": companies[0],
                "can_add_devices": False
            },
            {
                "email": "user1@techstart.com",
                "google_id": "user3_google_id",
                "full_name": "Carol Davis",
                "company": companies[1],
                "can_add_devices": True
            },
            {
                "email": "user1@globalretail.com",
                "google_id": "user4_google_id",
                "full_name": "David Martinez",
                "company": companies[2],
                "can_add_devices": True
            }
        ]

        users = []
        for user_data in users_data:
            company = user_data.pop('company')
            user = User(
                **user_data,
                role=UserRole.USER,
                company_id=company.id,
                is_active=True,
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.flush()
            users.append(user)
            print(f"   [OK] User created: {user.email} for {company.name}")

        # 5. Create Sample Devices
        print("\n[5] Creating sample devices...")

        devices_data = [
            {
                "user": users[0],  # Alice from Acme
                "company": companies[0],
                "device_name": "Main Lobby Display",
                "device_code": "1234",
                "device_id": "TV-ACME-001",
                "is_linked": True,
                "is_online": True
            },
            {
                "user": users[0],  # Alice from Acme
                "company": companies[0],
                "device_name": "Conference Room TV",
                "device_code": "5678",
                "device_id": "TV-ACME-002",
                "is_linked": True,
                "is_online": False
            },
            {
                "user": users[2],  # Carol from TechStart
                "company": companies[1],
                "device_name": "Reception Display",
                "device_code": "9012",
                "device_id": "TV-TECH-001",
                "is_linked": True,
                "is_online": True
            }
        ]

        for device_data in devices_data:
            user = device_data.pop('user')
            company = device_data.pop('company')
            device = Device(
                **device_data,
                user_id=user.id,
                company_id=company.id,
                last_seen=datetime.utcnow() if device_data.get('is_online') else None,
                linked_at=datetime.utcnow()
            )
            db.add(device)
            print(f"   [OK] Device created: {device.device_name} ({device.device_id})")

        # 6. Create Sample Invitations
        print("\n[6] Creating sample invitations...")

        invitations_data = [
            {
                "email": "newuser@acme.com",
                "role": UserRole.USER,
                "company": companies[0],
                "invited_by": admins[0],
                "status": InvitationStatus.PENDING
            },
            {
                "email": "newadmin@techstart.com",
                "role": UserRole.ADMIN,
                "company": companies[1],
                "invited_by": super_admin,
                "status": InvitationStatus.PENDING
            }
        ]

        for inv_data in invitations_data:
            company = inv_data.pop('company')
            invited_by = inv_data.pop('invited_by')
            invitation = Invitation(
                **inv_data,
                company_id=company.id,
                invited_by=invited_by.id,
                token=secrets.token_urlsafe(32),
                expires_at=datetime.utcnow() + timedelta(hours=72)
            )
            db.add(invitation)
            print(f"   [OK] Invitation created: {invitation.email} as {invitation.role.value}")

        # 7. Create Audit Logs
        print("\n[7] Creating sample audit logs...")

        audit_logs_data = [
            {
                "user": super_admin,
                "action": "user.login",
                "resource_type": "user",
                "resource_id": super_admin.id,
                "details": {"ip": "192.168.1.1", "user_agent": "Mozilla/5.0"}
            },
            {
                "user": admins[0],
                "action": "company.created",
                "resource_type": "company",
                "resource_id": companies[0].id,
                "details": {"company_name": companies[0].name}
            },
            {
                "user": users[0],
                "action": "device.linked",
                "resource_type": "device",
                "resource_id": None,
                "details": {"device_name": "Main Lobby Display"}
            }
        ]

        for log_data in audit_logs_data:
            user = log_data.pop('user')
            audit_log = AuditLog(
                **log_data,
                user_id=user.id,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            db.add(audit_log)
            print(f"   [OK] Audit log created: {audit_log.action}")

        # Commit all changes
        print("\n[*] Saving all data to database...")
        db.commit()

        print_header("Sample Data Created Successfully!")

        print("[*] Summary:")
        print(f"   - Super Admins: 1")
        print(f"   - Companies: {len(companies)}")
        print(f"   - Company Admins: {len(admins)}")
        print(f"   - Regular Users: {len(users)}")
        print(f"   - Devices: {len(devices_data)}")
        print(f"   - Pending Invitations: {len(invitations_data)}")
        print(f"   - Audit Logs: {len(audit_logs_data)}")

        print("\n[*] Test Credentials:")
        print("   Super Admin: admin@example.com")
        print("   Acme Admin:  admin@acme.com")
        print("   Acme User:   user1@acme.com")
        print("\n   Note: These are sample accounts for testing.")
        print("   For real login, use Google OAuth.\n")

    except Exception as e:
        print(f"\n[ERROR] Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def display_database_stats():
    """Display statistics about the database"""
    print_header("Database Statistics")

    from sqlalchemy.orm import Session
    engine = create_engine(settings.DATABASE_URL)
    db = Session(bind=engine)

    try:
        stats = {
            "Users": db.query(User).count(),
            "Companies": db.query(Company).count(),
            "Devices": db.query(Device).count(),
            "Invitations": db.query(Invitation).count(),
            "Audit Logs": db.query(AuditLog).count()
        }

        print("Current database contents:\n")
        for key, value in stats.items():
            print(f"   {key:.<30} {value:>5}")

        # Show user breakdown
        if stats["Users"] > 0:
            print("\n📊 User breakdown:")
            for role in UserRole:
                count = db.query(User).filter(User.role == role).count()
                if count > 0:
                    print(f"   {role.value:.<30} {count:>5}")

        print()

    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    finally:
        db.close()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Initialize local database for Simple Digital Signage"
    )
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Create sample data for testing'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop all tables and recreate (WARNING: deletes all data)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )

    args = parser.parse_args()

    print_header("Simple Digital Signage - Database Initialization")

    print(f"📍 Environment: {settings.APP_ENV}")
    print(f"🗄️  Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Unknown'}")
    print()

    # Check database connection
    engine = check_database_connection()
    if not engine:
        sys.exit(1)

    # Show stats only
    if args.stats:
        display_database_stats()
        return

    # Create tables
    if not create_tables(engine, reset=args.reset):
        sys.exit(1)

    # Create sample data if requested
    if args.sample_data:
        create_sample_data()

    # Show final stats
    display_database_stats()

    print_header("Setup Complete!")

    print("✅ Your database is ready to use!\n")
    print("🚀 Next steps:")
    print("   1. Start the application:")
    print("      python main.py")
    print()
    print("   2. Open the frontend:")
    print("      Open frontend/index.html in your browser")
    print()
    print("   3. Login with Google OAuth")
    print("      First user becomes Super Admin automatically")
    print()

    if args.sample_data:
        print("📝 Note: Sample data has been created for testing.")
        print("   You can explore the system with pre-populated data.\n")


if __name__ == "__main__":
    main()
