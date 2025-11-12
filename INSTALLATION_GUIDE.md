# Complete Installation & Startup Guide

This guide will walk you through every step to get your Simple Digital Signage backend running from scratch.

## Table of Contents

1. [Prerequisites Installation](#prerequisites-installation)
2. [Project Setup](#project-setup)
3. [Database Configuration](#database-configuration)
4. [Google OAuth Setup](#google-oauth-setup)
5. [Email Configuration](#email-configuration)
6. [Running the Application](#running-the-application)
7. [Testing the API](#testing-the-api)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites Installation

### 1. Install Python 3.8+

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
```bash
python --version
# Should show: Python 3.8.x or higher
```

**Mac:**
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv

# Verify
python3 --version
```

### 2. Install PostgreSQL

**Windows:**
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run installer (use default settings)
3. Remember your password!
4. Default port: 5432

**Mac:**
```bash
# Using Homebrew
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Install Git (Optional but Recommended)

**Windows:** Download from https://git-scm.com/download/win

**Mac:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

---

## Project Setup

### Step 1: Navigate to Project Directory

Open your terminal/command prompt:

```bash
cd "C:\Users\aggar\Desktop\akshit app"
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your prompt
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies

```bash
# Make sure venv is activated (you should see (venv) in prompt)
pip install -r requirements.txt

# This will install ~50 packages, might take 2-3 minutes
```

**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 sqlalchemy-2.0.25 ...
```

---

## Database Configuration

### Step 1: Create PostgreSQL Database

**Windows:**

Open SQL Shell (psql) from Start Menu:

```sql
-- You'll be prompted for password (use the one you set during installation)

-- Create database
CREATE DATABASE simple_digital_signage;

-- Verify it was created
\l

-- Exit
\q
```

**Mac/Linux:**

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Or just:
psql postgres
```

```sql
-- Create database
CREATE DATABASE simple_digital_signage;

-- Verify
\l

-- Exit
\q
```

### Step 2: Configure Environment Variables

1. **Copy the template:**

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

2. **Edit the .env file:**

Open `.env` in any text editor (Notepad, VS Code, etc.)

**Update these critical settings:**

```bash
# ============================================================
# Database Configuration
# ============================================================
# Replace 'password' with your PostgreSQL password
DATABASE_URL=postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/simple_digital_signage

# ============================================================
# Security Keys (MUST CHANGE!)
# ============================================================
# Generate using: openssl rand -hex 32
SECRET_KEY=REPLACE_WITH_GENERATED_KEY
ENCRYPTION_KEY=REPLACE_WITH_GENERATED_KEY

# ============================================================
# Google OAuth (Will configure in next section)
# ============================================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ============================================================
# Email Configuration (Will configure later)
# ============================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Simple Digital Signage
```

### Step 3: Generate Security Keys

**Option 1: Using OpenSSL (Recommended)**

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Copy the output and paste into .env for SECRET_KEY

# Generate ENCRYPTION_KEY
openssl rand -hex 32

# Copy the output and paste into .env for ENCRYPTION_KEY
```

**Option 2: Using Python**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output to SECRET_KEY

python -c "import secrets; print(secrets.token_hex(32))"
# Copy output to ENCRYPTION_KEY
```

**Option 3: Using Online Generator**
- Go to: https://generate-secret.vercel.app/64
- Copy the key
- Paste into your `.env` file

---

## Google OAuth Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project:**
   - Click "Select a project" at the top
   - Click "NEW PROJECT"
   - Project name: "Simple Digital Signage"
   - Click "CREATE"
   - Wait for project creation (30 seconds)

3. **Select Your Project:**
   - Click "Select a project" again
   - Choose "Simple Digital Signage"

### Step 2: Enable Required APIs

1. **Enable Google+ API:**
   - In the left menu, click "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click on it
   - Click "ENABLE"
   - Wait for activation

2. **Enable People API (optional but recommended):**
   - Search for "People API"
   - Click on it
   - Click "ENABLE"

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth consent screen:**
   - Left menu: "APIs & Services" → "OAuth consent screen"

2. **Choose User Type:**
   - Select "External"
   - Click "CREATE"

3. **Fill in App Information:**
   - App name: `Simple Digital Signage`
   - User support email: Your email
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE"

4. **Scopes:**
   - Click "ADD OR REMOVE SCOPES"
   - Select:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
     - `openid`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test users (for External apps):**
   - Click "ADD USERS"
   - Add your email address
   - Click "SAVE AND CONTINUE"

6. **Review and Submit:**
   - Click "BACK TO DASHBOARD"

### Step 4: Create OAuth Credentials

1. **Go to Credentials:**
   - Left menu: "APIs & Services" → "Credentials"
   - Click "CREATE CREDENTIALS"
   - Select "OAuth client ID"

2. **Configure OAuth Client:**
   - Application type: "Web application"
   - Name: "Digital Signage Web Client"

3. **Add Authorized Redirect URIs:**
   - Click "ADD URI"
   - Enter: `http://localhost:8000/api/v1/auth/google/callback`
   - Click "CREATE"

4. **Copy Credentials:**
   - A popup will show your credentials
   - Copy "Client ID" → Paste into `.env` as `GOOGLE_CLIENT_ID`
   - Copy "Client Secret" → Paste into `.env` as `GOOGLE_CLIENT_SECRET`
   - Click "OK"

**Your .env should now have:**
```bash
GOOGLE_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123xyz789
```

---

## Email Configuration

### Option 1: Gmail (Recommended for Development)

1. **Enable 2-Step Verification:**
   - Go to: https://myaccount.google.com/security
   - Find "2-Step Verification"
   - Follow steps to enable it

2. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" → Type "Digital Signage"
   - Click "GENERATE"
   - Copy the 16-character password

3. **Update .env:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # The 16-char password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Simple Digital Signage
```

### Option 2: Other SMTP Providers

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Outlook:**
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

---

## Running the Application

### Step 1: Verify Setup

Run the verification script:

```bash
# Make sure venv is activated
python test_setup.py
```

**Expected output:**
```
============================================================
        Simple Digital Signage - Setup Verification
============================================================

Testing your setup...

Critical Checks:
✓ PASS | Python Version
         → Python 3.11.0
✓ PASS | Python Dependencies
         → All 7 required packages installed
✓ PASS | Environment Variables
         → All required environment variables configured
✓ PASS | Database Connection
         → Database connection successful
✓ PASS | Encryption System
         → Encryption working correctly

Optional Checks:
✗ FAIL | Database Tables
         → Missing tables: users, companies, ... (run the app once to create)
✓ PASS | Email Configuration
         → Email configured (smtp.gmail.com)
```

If database tables are missing, that's OK - they'll be created automatically.

### Step 2: Start the Application

```bash
# Make sure you're in the project directory and venv is activated
python main.py
```

**Expected output:**
```
INFO:     Starting Simple Digital Signage v1.0.0
INFO:     Environment: development
INFO:     Encryption key validated
INFO:     Database connection established
INFO:     Database initialized
INFO:     Application started successfully on 0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

🎉 **Success! Your backend is running!**

### Step 3: Verify It's Working

Open your browser and visit:

1. **API Documentation:** http://localhost:8000/api/docs
   - Should show interactive API documentation

2. **Health Check:** http://localhost:8000/api/v1/health
   - Should show: `{"status":"healthy","service":"Simple Digital Signage","version":"1.0.0"}`

3. **Root Endpoint:** http://localhost:8000
   - Should show app information

---

## Testing the API

### Method 1: Using Browser (Interactive Docs)

1. **Open:** http://localhost:8000/api/docs

2. **Test Health Check:**
   - Find "Health" section
   - Click on `GET /api/v1/health`
   - Click "Try it out"
   - Click "Execute"
   - Should see Status 200 with response

3. **Authenticate:**
   - Click on `GET /api/v1/auth/google/login`
   - Click "Try it out"
   - Click "Execute"
   - Copy the `auth_url` from response
   - Open that URL in a new tab
   - Login with Google
   - You'll be redirected back with tokens

4. **Use Your Token:**
   - Copy the `access_token` from the response
   - Click "Authorize" button at top of docs page
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"
   - Now you can test protected endpoints!

### Method 2: Using cURL (Command Line)

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health

# 2. Get Google OAuth URL
curl http://localhost:8000/api/v1/auth/google/login

# 3. After getting token, check your profile
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Create a company (Super Admin only)
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

### Method 3: Using Postman

1. **Download Postman:** https://www.postman.com/downloads/
2. **Import Collection:**
   - Create new collection: "Digital Signage API"
   - Add request: GET http://localhost:8000/api/v1/health
   - Add request: GET http://localhost:8000/api/v1/auth/google/login
3. **Set up Authorization:**
   - In collection settings
   - Auth Type: "Bearer Token"
   - Token: Your access_token

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# If not activated:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Then install dependencies:
pip install -r requirements.txt
```

### Issue 2: "Could not connect to database"

**Solution:**
```bash
# Check if PostgreSQL is running
# Windows: Check Services
# Mac: brew services list
# Linux: sudo systemctl status postgresql

# Verify database exists
psql -U postgres -l

# Check DATABASE_URL in .env
# Make sure password is correct
```

### Issue 3: "Invalid client_id" during Google OAuth

**Solution:**
- Verify `GOOGLE_CLIENT_ID` in `.env` matches Google Cloud Console
- Check redirect URI matches exactly: `http://localhost:8000/api/v1/auth/google/callback`
- Make sure Google+ API is enabled

### Issue 4: "Failed to send email"

**Solution:**
- For Gmail: Use App Password, not regular password
- Enable "Less secure app access" (if not using App Password)
- Check SMTP settings in `.env`
- Test with: `python -c "from app.utils.email import send_test_email; send_test_email('your-email@gmail.com')"`

### Issue 5: Port 8000 already in use

**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Or change port in .env:
PORT=8080
```

### Issue 6: "Invalid or expired token"

**Solution:**
- Tokens expire after 30 minutes
- Use refresh token to get new access token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

## Next Steps

Now that your backend is running:

1. ✅ **Create your first Super Admin account:**
   - Visit: http://localhost:8000/api/v1/auth/google/login
   - Login with Google
   - First user becomes Super Admin automatically

2. ✅ **Create a company:**
   - Use the API docs or cURL
   - POST to `/api/v1/companies`

3. ✅ **Invite users:**
   - POST to `/api/v1/invitations`
   - They'll receive email invitation

4. ✅ **Explore the API:**
   - Interactive docs: http://localhost:8000/api/docs
   - Try different endpoints

5. ✅ **Build a frontend:**
   - See `FRONTEND_GUIDE.md` (next section)
   - Connect to this backend

---

## Stopping the Application

Press `CTRL + C` in the terminal where the app is running.

To deactivate virtual environment:
```bash
deactivate
```

---

## Quick Reference

**Start Application:**
```bash
cd "C:\Users\aggar\Desktop\akshit app"
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
python main.py
```

**Important URLs:**
- API Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/v1/health
- Google Login: http://localhost:8000/api/v1/auth/google/login

**Important Files:**
- `.env` - Configuration
- `main.py` - Application entry
- `requirements.txt` - Dependencies

**Get Help:**
- Check logs in terminal
- Visit: http://localhost:8000/api/docs
- Read: README.md

---

🎉 **Congratulations! Your backend is now running!**

Next: See the FRONTEND_GUIDE.md to build a basic UI.
