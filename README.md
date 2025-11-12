# Simple Digital Signage Backend

A comprehensive FastAPI backend for managing digital signage across Smart TVs with multi-tenant support, Google Drive integration, and role-based access control.

## Features

✅ **Multi-Tenant Architecture**
- Super Admin, Company Admin, and User roles
- Complete data isolation between companies
- Configurable user and device limits per company

✅ **Authentication & Security**
- Google OAuth SSO integration
- JWT-based authentication (access + refresh tokens)
- AES-256-GCM encryption for sensitive data
- Role-based access control (RBAC)

✅ **Device Management**
- Smart TV device pairing with 4-digit codes
- Device linking and unlinking
- Real-time device status monitoring
- WebSocket support (pending implementation)

✅ **User Management**
- User invitation system with email notifications
- Permission management
- User activation/deactivation
- Profile management

✅ **Google Drive Integration**
- Per-company Google Cloud credentials
- Per-user Google Drive OAuth tokens
- Secure credential storage

✅ **Email Service**
- Invitation emails with branded templates
- Welcome emails
- Device linked notifications
- SMTP support (Gmail, SendGrid, AWS SES)

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy ORM 2.0.25
- **Authentication**: JWT with python-jose
- **Encryption**: AES-256-GCM with cryptography library
- **Email**: SMTP with HTML templates
- **Background Tasks**: Celery with Redis (configured)
- **Server**: Uvicorn ASGI server

## Project Structure

```
akshit app/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── DATABASE_SCHEMA.md     # Database schema documentation
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection & session
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── device.py
│   │   ├── invitation.py
│   │   ├── google_credential.py
│   │   ├── google_drive_token.py
│   │   └── audit_log.py
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── users.py       # User management
│   │   ├── companies.py   # Company management
│   │   ├── devices.py     # Device management
│   │   ├── invitations.py # Invitation system
│   │   ├── google_drive.py # Google Drive integration
│   │   └── health.py      # Health checks
│   ├── schemas/           # Pydantic validation schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── company.py
│   │   └── invitation.py
│   └── utils/             # Utility functions
│       ├── auth.py        # JWT & RBAC utilities
│       ├── encryption.py  # AES-256 encryption
│       └── email.py       # Email sending service
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Google Cloud Project (for OAuth)
- SMTP server credentials (Gmail, SendGrid, etc.)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE simple_digital_signage;
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required settings:**

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/simple_digital_signage

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### 5. Generate Secret Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
openssl rand -hex 32
```

### 6. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
6. Copy Client ID and Client Secret to `.env`

### 7. Run the Application

```bash
# Development mode
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Authentication
- `GET /api/v1/auth/google/login` - Initiate Google OAuth
- `GET /api/v1/auth/google/callback` - OAuth callback
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

### Companies (Super Admin Only)
- `POST /api/v1/companies` - Create company
- `GET /api/v1/companies` - List companies
- `GET /api/v1/companies/{id}` - Get company details
- `PUT /api/v1/companies/{id}` - Update company
- `DELETE /api/v1/companies/{id}` - Delete company
- `POST /api/v1/companies/{id}/deactivate` - Deactivate company
- `GET /api/v1/companies/{id}/stats` - Company statistics

### Users
- `GET /api/v1/users` - List users (with filters)
- `GET /api/v1/users/me` - Get own profile
- `PUT /api/v1/users/me` - Update own profile
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user (Admin)
- `PUT /api/v1/users/{id}/permissions` - Update permissions
- `POST /api/v1/users/{id}/deactivate` - Deactivate user
- `DELETE /api/v1/users/{id}` - Delete user

### Devices
- `POST /api/v1/devices/generate-code` - Generate pairing code
- `POST /api/v1/devices/link` - Link device to account
- `GET /api/v1/devices/my-devices` - Get user's devices
- `DELETE /api/v1/devices/{id}` - Unlink device

### Invitations (Admin Only)
- `POST /api/v1/invitations` - Send invitation
- `GET /api/v1/invitations` - List invitations
- `DELETE /api/v1/invitations/{id}` - Cancel invitation

### Health
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status
- `GET /api/v1/health/ready` - Readiness probe (Kubernetes)
- `GET /api/v1/health/live` - Liveness probe (Kubernetes)

## User Roles & Permissions

### Super Admin
- Manage all companies
- Create/delete companies
- View all users and devices across companies
- System-wide access

### Company Admin
- Invite and manage users in their company
- Set user permissions
- View company statistics
- Manage company devices

### User
- Link Google Drive account
- Add devices (if permission granted)
- Manage own content and playlists
- View own data only

## Testing

### Test Database Connection
```bash
python -c "from app.database import check_db_connection; print('DB:', check_db_connection())"
```

### Test Encryption
```bash
python -c "from app.utils.encryption import test_encryption; test_encryption()"
```

### Test Email
```bash
python -c "from app.utils.email import send_test_email; send_test_email('your-email@example.com')"
```

### Access API Documentation
Open your browser to http://localhost:8000/api/docs

## First Time Setup

### Create First Super Admin

The first user to log in via Google OAuth will automatically be created as a Super Admin.

1. Start the server
2. Navigate to http://localhost:8000/api/v1/auth/google/login
3. Complete Google OAuth
4. You'll be logged in as Super Admin

### Create Your First Company

```bash
curl -X POST "http://localhost:8000/api/v1/companies" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Company",
    "subdomain": "mycompany",
    "max_users": 50,
    "max_devices": 100
  }'
```

### Invite Company Admin

```bash
curl -X POST "http://localhost:8000/api/v1/invitations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "role": "admin"
  }'
```

## Development

### Running in Debug Mode

Set in `.env`:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### Database Migrations (Todo)

Alembic migrations need to be initialized:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

## Security Considerations

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Change default keys** - Always generate new SECRET_KEY and ENCRYPTION_KEY
3. **Use HTTPS in production** - Never send tokens over HTTP
4. **Rotate tokens regularly** - Implement token refresh mechanism
5. **Rate limiting** - Configure rate limiting in production
6. **Database backups** - Regular backups of PostgreSQL database
7. **Audit logging** - Monitor all sensitive operations

## Production Deployment

### Recommended Stack
- **Load Balancer**: Nginx or AWS ALB
- **Application**: Docker container with Uvicorn
- **Database**: PostgreSQL (RDS or managed instance)
- **Caching**: Redis for Celery and session management
- **Monitoring**: Sentry for error tracking
- **Logging**: ELK stack or CloudWatch

### Environment Variables for Production
```bash
APP_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@prod-db:5432/db
CORS_ORIGINS=https://yourdomain.com
ENABLE_RATE_LIMITING=True
ENABLE_MONITORING=True
SENTRY_DSN=your-sentry-dsn
```

### Docker Deployment (Example)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists

### Google OAuth Errors
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Check redirect URI matches Google Console
- Ensure Google+ API is enabled

### Email Not Sending
- Verify SMTP credentials
- For Gmail, use App Password (not regular password)
- Check SMTP_HOST and SMTP_PORT

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

## TODO / Roadmap

- [ ] Implement WebSocket endpoints for real-time device updates
- [ ] Add audit logging middleware
- [ ] Create Alembic database migrations
- [ ] Implement content management (images/videos)
- [ ] Add playlist management
- [ ] Implement Celery background tasks
- [ ] Add comprehensive test suite
- [ ] Implement rate limiting
- [ ] Add API versioning
- [ ] Create admin dashboard
- [ ] Add analytics and reporting
- [ ] Implement content caching
- [ ] Add device remote control features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

Copyright © 2024 Simple Digital Signage. All rights reserved.

## Support

For issues and questions:
- Check documentation: `/api/docs`
- Review code comments
- Check logs for errors

---

**Built with FastAPI and ❤️**
