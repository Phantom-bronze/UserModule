# Quick Start Guide

Get your Simple Digital Signage backend running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] PostgreSQL installed and running
- [ ] Google Cloud account (for OAuth)
- [ ] Gmail or SMTP credentials (for email)

## Step-by-Step Setup

### 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### 2. Create Database (1 minute)

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE simple_digital_signage;

# Exit
\q
```

### 3. Configure Environment (2 minutes)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set the minimum required values:

```bash
# Database - Update with your PostgreSQL credentials
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/simple_digital_signage

# Security - Generate these keys
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Google OAuth - Get from Google Cloud Console
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Email - Use your Gmail credentials
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

### 4. Google OAuth Setup (2 minutes)

1. Go to https://console.cloud.google.com
2. Create new project: "Digital Signage"
3. Navigate to: APIs & Services → Credentials
4. Click "Create Credentials" → "OAuth client ID"
5. Application type: "Web application"
6. Add redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
7. Copy Client ID and Client Secret to your `.env` file

### 5. Gmail App Password (for email)

1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other" → "Digital Signage"
4. Copy the generated password to `SMTP_PASSWORD` in `.env`

### 6. Run the Application!

```bash
python main.py
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 7. Test the API

Open your browser to:

- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/v1/health

## First Login

### Become Super Admin

1. Navigate to: http://localhost:8000/api/v1/auth/google/login
2. You'll be redirected to Google login
3. Authorize the application
4. You'll be redirected back and logged in
5. **The first user becomes Super Admin automatically!**

### Get Your Access Token

After successful OAuth, you'll receive a JSON response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "...",
    "email": "your-email@gmail.com",
    "role": "super_admin"
  }
}
```

Copy the `access_token` for API requests.

## Quick API Tests

### 1. Check Your Profile

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Create a Company

```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "subdomain": "test",
    "max_users": 10,
    "max_devices": 20
  }'
```

### 3. Send an Invitation

```bash
curl -X POST http://localhost:8000/api/v1/invitations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "admin"
  }'
```

### 4. List Users

```bash
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Using the Interactive API Docs

1. Go to http://localhost:8000/api/docs
2. Click the "Authorize" button at the top right
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize"
5. Now you can test all endpoints interactively!

## Troubleshooting

### Database Connection Error

```
Could not connect to database
```

**Fix:**
- Check PostgreSQL is running: `pg_ctl status`
- Verify DATABASE_URL in `.env`
- Test connection: `psql -U postgres simple_digital_signage`

### Google OAuth Error

```
Invalid client_id or redirect_uri
```

**Fix:**
- Verify GOOGLE_CLIENT_ID in `.env`
- Check redirect URI matches: `http://localhost:8000/api/v1/auth/google/callback`
- Enable Google+ API in Google Cloud Console

### Email Not Sending

```
Failed to send email
```

**Fix:**
- For Gmail, use an App Password (not your regular password)
- Enable "Less secure app access" or use OAuth2
- Check SMTP_USERNAME and SMTP_PASSWORD in `.env`

### Import Errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:**
```bash
pip install -r requirements.txt
```

## Next Steps

Now that your backend is running:

1. **Explore the API** - Use the interactive docs at `/api/docs`
2. **Create companies** - Set up organizations
3. **Invite users** - Send invitations to team members
4. **Pair devices** - Test device pairing flow
5. **Integrate frontend** - Connect your React/Vue/Angular frontend

## Common Tasks

### Reset Database

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE simple_digital_signage;"
psql -U postgres -c "CREATE DATABASE simple_digital_signage;"

# Restart application (tables will be created automatically)
python main.py
```

### Generate New Secret Keys

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### View Logs

The application logs to console by default. For production, configure:

```bash
# In .env
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log
```

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Development Mode

Enable debug mode for detailed error messages:

```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

Restart the server and you'll see:
- Detailed SQL queries
- Full error stack traces
- Request/response logging

## Production Checklist

Before deploying to production:

- [ ] Generate new SECRET_KEY and ENCRYPTION_KEY
- [ ] Set DEBUG=False
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Use environment-specific settings
- [ ] Implement proper logging
- [ ] Set up CI/CD pipeline

## Need Help?

- **API Documentation**: http://localhost:8000/api/docs
- **Code Documentation**: Check inline comments in source code
- **Database Schema**: See `DATABASE_SCHEMA.md`
- **Full Documentation**: See `README.md`

---

Happy coding! 🚀
