# Simple Digital Signage - Complete Setup Guide

This guide will help you set up and run the Simple Digital Signage application on your local machine in under 15 minutes.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, make sure you have the following installed:

### 1. Python 3.8 or higher
```bash
# Check Python version
python --version
# or
python3 --version
```

If you don't have Python installed, download it from [python.org](https://www.python.org/downloads/)

### 2. PostgreSQL 12 or higher
```bash
# Check PostgreSQL version
psql --version
```

If you don't have PostgreSQL:
- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: Use Homebrew: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 3. Git (Optional, if cloning from repository)
```bash
git --version
```

## Quick Start

### Step 1: Install PostgreSQL and Create Database

1. **Install PostgreSQL** (if not already installed)
   - Follow the official installation guide for your OS
   - Remember the password you set for the `postgres` user

2. **Create the database**:
   ```bash
   # Login to PostgreSQL (Windows: use pgAdmin or command prompt)
   psql -U postgres

   # Create database
   CREATE DATABASE digital_signage;

   # Exit psql
   \q
   ```

### Step 2: Clone or Extract the Project

If you have the project as a ZIP file, extract it. If it's in a Git repository:
```bash
git clone <repository-url>
cd UserManagementModule
```

### Step 3: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

1. **Copy the example environment file**:
   ```bash
   # Windows
   copy .env.example .env

   # macOS/Linux
   cp .env.example .env
   ```

2. **Edit `.env` file** with your settings:
   ```bash
   # Required changes:

   # 1. Database URL (update password if different)
   DATABASE_URL=postgresql+pg8000://postgres:YOUR_PASSWORD@localhost:5432/digital_signage

   # 2. Generate secret keys
   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
   ENCRYPTION_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">

   # 3. Google OAuth Credentials (from Google Cloud Console)
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### Step 6: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
   - Click "Create"
5. Copy the Client ID and Client Secret to your `.env` file

### Step 7: Initialize the Database

```bash
python init_local_db.py
```

This script will:
- Test database connection
- Create all necessary tables
- Set up the schema

### Step 8: Run the Application

```bash
python main.py
```

You should see output like:
```
INFO: Frontend UI mounted at / from .../frontend
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: Database connection established
INFO: Application started successfully on 0.0.0.0:8000
```

### Step 9: Access the Application

Open your web browser and go to:
```
http://localhost:8000
```

### Step 10: Create Your First Admin Account

1. Click "Sign in with Google"
2. Complete the Google OAuth flow
3. You'll automatically be created as the Super Admin (first user)

**Congratulations! Your application is now running!**

## Detailed Setup

### Generating Secret Keys

The application requires two secret keys for security:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy these values to your `.env` file.

### Database Configuration Options

The application uses the `pg8000` driver for PostgreSQL, which provides better cross-platform compatibility:

```env
# Standard format
DATABASE_URL=postgresql+pg8000://username:password@host:port/database_name

# Example configurations:
# Local PostgreSQL
DATABASE_URL=postgresql+pg8000://postgres:postgres@localhost:5432/digital_signage

# Remote PostgreSQL
DATABASE_URL=postgresql+pg8000://user:pass@remote-host:5432/digital_signage
```

### Email Configuration (Optional)

If you want to send invitation emails:

1. For Gmail:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=True
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password  # Not your regular password!
   FROM_EMAIL=noreply@yourdomain.com
   ```

2. Generate a Gmail App Password:
   - Go to your Google Account settings
   - Enable 2-factor authentication
   - Go to Security > App passwords
   - Generate a new app password
   - Use this password in `.env`

## Running the Application

### Development Mode (with auto-reload)

```bash
python main.py
```

This starts the server with auto-reload enabled, so changes to your code will automatically restart the server.

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Virtual Environment

Always activate your virtual environment before running:

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Then run the application
python main.py
```

### Stopping the Application

Press `CTRL+C` in the terminal where the application is running.

## Troubleshooting

### Issue: Database Connection Failed

**Problem**: `sqlalchemy.exc.OperationalError` or connection refused

**Solutions**:
1. Check if PostgreSQL is running:
   ```bash
   # Windows
   services.msc  # Look for postgresql service

   # macOS
   brew services list

   # Linux
   sudo systemctl status postgresql
   ```

2. Verify database exists:
   ```bash
   psql -U postgres -l
   ```

3. Check DATABASE_URL in `.env` file:
   - Correct username/password
   - Correct database name
   - Correct host and port

### Issue: Google OAuth Error

**Problem**: "Access blocked: Authorization Error"

**Solutions**:
1. Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in `.env`
2. Check redirect URI matches Google Console: `http://localhost:8000/api/v1/auth/google/callback`
3. Ensure Google+ API is enabled in Google Cloud Console
4. Use full URL scopes in .env:
   ```env
   GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile
   ```

### Issue: Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
1. Activate virtual environment:
   ```bash
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Issue: Port Already in Use

**Problem**: `OSError: [Errno 98] Address already in use`

**Solutions**:
1. Check what's using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000

   # macOS/Linux
   lsof -i :8000
   ```

2. Kill the process or use a different port:
   ```env
   # In .env file
   PORT=8001
   ```

### Issue: SQLAlchemy Mapper Errors

**Problem**: `mapper 'User' failed to locate a name`

**Solution**: This was already fixed! Make sure you're using the latest version of the code where GoogleDriveToken and GoogleCredential relationships are commented out.

## Next Steps

### 1. Explore the Application

- **Dashboard**: View system health and statistics
- **Companies**: Create and manage companies (Super Admin only)
- **Users**: View and manage users
- **Devices**: Link Smart TV devices
- **Invitations**: Send invitations to new users

### 2. Create Your First Company

As Super Admin, you can create companies:
1. Go to Companies page
2. Click "+ New Company"
3. Fill in company details

### 3. Invite Users

1. Go to Invitations page
2. Click "+ Send Invitation"
3. Enter email and select role
4. Invited user will receive an email (if SMTP configured)

### 4. API Documentation

Access the interactive API documentation:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 5. Testing API Endpoints

You can test API endpoints using:
- The built-in Swagger UI
- curl commands
- Postman
- Any HTTP client

Example curl command:
```bash
curl -X GET "http://localhost:8000/api/v1/health" -H "accept: application/json"
```

## Configuration Reference

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DATABASE_URL | PostgreSQL connection URL | Yes | - |
| SECRET_KEY | JWT secret key | Yes | - |
| ENCRYPTION_KEY | AES encryption key | Yes | - |
| GOOGLE_CLIENT_ID | Google OAuth Client ID | Yes | - |
| GOOGLE_CLIENT_SECRET | Google OAuth Client Secret | Yes | - |
| GOOGLE_REDIRECT_URI | OAuth callback URL | Yes | http://localhost:8000/api/v1/auth/google/callback |
| GOOGLE_SCOPES | OAuth permission scopes | Yes | See .env.example |
| PORT | Server port | No | 8000 |
| HOST | Server host | No | 0.0.0.0 |
| DEBUG | Debug mode | No | True |
| CORS_ORIGINS | Allowed CORS origins | No | localhost:3000,8000,8080,8100 |

### Database Schema

The application automatically creates these tables:
- **users**: User accounts and authentication
- **companies**: Multi-tenant company information
- **devices**: Smart TV device registrations
- **invitations**: User invitation tokens
- **audit_logs**: Activity logging

For detailed schema information, see [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Generate unique SECRET_KEY and ENCRYPTION_KEY** - Don't use defaults
3. **Use environment-specific configurations** - Different keys for dev/prod
4. **Enable HTTPS in production** - Never send tokens over HTTP
5. **Keep dependencies updated** - Regularly run `pip install --upgrade -r requirements.txt`
6. **Backup your database** - Regular PostgreSQL backups
7. **Rotate tokens regularly** - Implement token refresh mechanism

## Getting Help

If you encounter issues:

1. **Check logs**: Look at the console output for error messages
2. **Verify configuration**: Double-check your `.env` file
3. **Test connections**: Use the provided test scripts
4. **Read documentation**: Check [README.md](README.md) and [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
5. **Check database**: Verify tables were created with `\dt` in psql

## Platform-Specific Notes

### Windows

- Use Command Prompt or PowerShell
- PostgreSQL is usually installed via the installer
- Virtual environment activation: `.venv\Scripts\activate`
- Path separators use backslash `\`

### macOS

- Use Terminal
- PostgreSQL can be installed via Homebrew
- Virtual environment activation: `source .venv/bin/activate`
- May need to use `python3` instead of `python`

### Linux

- Use Terminal
- PostgreSQL installation varies by distribution
- Virtual environment activation: `source .venv/bin/activate`
- May need `python3` and `pip3` commands

## Summary

You've successfully set up the Simple Digital Signage application! Here's what you accomplished:

- ✅ Installed and configured PostgreSQL
- ✅ Set up Python virtual environment
- ✅ Installed all dependencies
- ✅ Configured environment variables
- ✅ Set up Google OAuth
- ✅ Initialized the database
- ✅ Started the application
- ✅ Created your admin account

The application is now running at http://localhost:8000 and ready to use!

---

**Need help?** Check the troubleshooting section above or review the logs for error messages.
