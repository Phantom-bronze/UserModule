# Quick Start Guide - User Management Module

## Prerequisites Checklist
Before starting, ensure you have:
- ✅ Python 3.8+ installed
- ✅ PostgreSQL 12+ installed and running
- ✅ Database `digital_signage` created
- ✅ Google OAuth credentials configured

---

## Step-by-Step Instructions

### 1. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Verify Configuration
Check your `.env` file has these required values:
```env
DATABASE_URL=postgresql+pg8000://postgres:YOUR_PASSWORD@localhost:5432/digital_signage
SECRET_KEY=<your-secret-key>
ENCRYPTION_KEY=<your-encryption-key>
GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-client-secret>
```

### 3. Initialize Database (First Time Only)
```bash
python init_local_db.py
```

### 4. Start the Application
```bash
# Option 1: Using the run script (Windows)
run_local.bat

# Option 2: Using Python directly
python main.py
```

### 5. Access the Application
Open your browser and go to:
```
http://localhost:8000
```

### 6. First Login
1. Click "Sign in with Google"
2. Complete Google OAuth flow
3. You'll be created as the **Super Admin** (first user)

---

## Key Features Available

### For Super Admins
After logging in as super admin, you can:

#### 1. View System Overview
- Navigate to: **Overview** tab
- See system health and statistics

#### 2. Manage Companies
- Navigate to: **Companies** tab
- Click: **+ New Company**
- Create and configure companies

#### 3. Manage Users ⭐ NEW FEATURE
- Navigate to: **Users** tab
- Click: **+ Add User** button
- Fill in the form:
  - Email address (required)
  - Full name (required)
  - Role (User or Admin)
  - Company (select from dropdown)
  - Can add devices (checkbox)
- Click: **Create User**
- User is created instantly!

#### 4. Manage Devices
- Navigate to: **Devices** tab
- Link Smart TV devices using pairing codes

#### 5. Send Invitations
- Navigate to: **Invitations** tab
- Send invitation emails to new users

---

## Testing the New User Creation Feature

### Test Case 1: Create a Regular User
1. Go to **Users** tab
2. Click **+ Add User**
3. Enter:
   - Email: `testuser@example.com`
   - Full Name: `Test User`
   - Role: `User`
   - Company: Select any company
   - Can add devices: ☑️ (checked)
4. Click **Create User**
5. ✅ Success toast should appear
6. ✅ User should appear in the list

### Test Case 2: Create an Admin User
1. Click **+ Add User** again
2. Enter:
   - Email: `admin@company.com`
   - Full Name: `Company Admin`
   - Role: `Admin`
   - Company: Select a company
   - Can add devices: ☑️ (checked)
3. Click **Create User**
4. ✅ Admin user created successfully

### Test Case 3: Validate Duplicate Email
1. Try creating a user with the same email
2. ✅ Should see error: "User with this email already exists"

---

## API Testing

### Using Swagger UI
1. Open: http://localhost:8000/api/docs
2. Expand: **Users** section
3. Find: **POST /api/v1/users**
4. Click: **Try it out**
5. Fill in the request body
6. Click: **Execute**

### Using curl
```bash
# First, get your access token from localStorage after logging in
# Then use it in the Authorization header

curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "New User",
    "role": "user",
    "company_id": "COMPANY_UUID",
    "can_add_devices": true
  }'
```

---

## Common Commands

### Stop the Application
```bash
Press Ctrl+C in the terminal
```

### Restart the Application
```bash
python main.py
```

### View Logs
Logs are displayed in the terminal where you started the application.

### Check Database Connection
```bash
python -c "from app.database import check_db_connection; print('Connected!' if check_db_connection() else 'Failed')"
```

### Reset Database (⚠️ WARNING: Deletes all data)
```bash
python init_local_db.py
```

---

## Troubleshooting

### Problem: "Add User" button not visible
**Solution**:
- Only **Super Admins** can see this button
- Make sure you're logged in as the first user (super admin)
- Check user role in the sidebar

### Problem: "Company has reached maximum user limit"
**Solution**:
1. Go to database and update company limits:
```sql
UPDATE companies SET max_users = 50 WHERE id = 'company-uuid';
```
Or modify in `.env`:
```env
DEFAULT_MAX_USERS_PER_COMPANY=50
```

### Problem: Modal doesn't open
**Solution**:
- Check browser console for JavaScript errors
- Refresh the page (Ctrl+F5)
- Clear browser cache

### Problem: Form submission fails
**Solution**:
- Check if you're still authenticated (token might have expired)
- Log out and log back in
- Check network tab in browser DevTools for detailed error

---

## Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8000 | Main application UI |
| API Docs (Swagger) | http://localhost:8000/api/docs | Interactive API documentation |
| API Docs (ReDoc) | http://localhost:8000/api/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/api/v1/health | Basic health endpoint |
| Detailed Health | http://localhost:8000/api/v1/health/detailed | Detailed system status |

---

## Database Access

### Connect to PostgreSQL
```bash
# Windows
psql -U postgres -d digital_signage

# macOS/Linux
psql -U postgres -d digital_signage
```

### Useful SQL Queries

**View all users:**
```sql
SELECT id, email, full_name, role, is_active FROM users;
```

**View all companies:**
```sql
SELECT id, name, max_users, is_active FROM companies;
```

**Count users per company:**
```sql
SELECT c.name, COUNT(u.id) as user_count, c.max_users
FROM companies c
LEFT JOIN users u ON c.id = u.company_id
GROUP BY c.id, c.name, c.max_users;
```

**View recent audit logs:**
```sql
SELECT created_at, action, resource_type, details
FROM audit_logs
ORDER BY created_at DESC
LIMIT 10;
```

---

## Next Steps

### 1. Create Your First Company
Required before adding users (unless user is super admin without company).

### 2. Add Users
Use the new **+ Add User** feature to add team members.

### 3. Configure Permissions
Set user permissions for device management.

### 4. Link Devices
Have users link their Smart TV devices.

### 5. Explore API
Check out the interactive API documentation at `/api/docs`.

---

## Important Notes

### Security
- 🔒 Never share your `.env` file
- 🔒 Keep SECRET_KEY and ENCRYPTION_KEY secure
- 🔒 First user is always Super Admin
- 🔒 Only Super Admins can create users via UI

### Data
- 💾 Database is persistent (data survives restarts)
- 💾 To reset data, re-run `init_local_db.py`
- 💾 Always backup before major changes

### Development
- 🔄 Application auto-reloads on code changes
- 🔄 Frontend changes require browser refresh
- 🔄 Database schema changes require migration

---

## Quick Reference Card

### Essential Commands
```bash
# Activate environment
.venv\Scripts\activate

# Start app
python main.py

# Initialize DB
python init_local_db.py

# Check health
curl http://localhost:8000/api/v1/health
```

### Essential Endpoints
- Login: http://localhost:8000/api/v1/auth/google/login
- Users: http://localhost:8000/api/v1/users
- Health: http://localhost:8000/api/v1/health

### User Roles
- **Super Admin**: Full system access, can create companies and users
- **Admin**: Manage users within their company
- **User**: Manage own content and devices

---

## Getting Help

If you encounter issues:
1. Check `CHANGES_SUMMARY.md` for recent changes
2. Read `SETUP_GUIDE.md` for detailed setup
3. Check `TESTING_GUIDE.md` for testing procedures
4. Review console/terminal logs for errors
5. Check browser console (F12) for frontend errors

---

## Summary

You now have a fully functional user management system with:
- ✅ Google OAuth authentication
- ✅ Multi-tenant company support
- ✅ Role-based access control
- ✅ **NEW**: Direct user creation UI for super admins
- ✅ Device management
- ✅ User invitations
- ✅ Comprehensive API

**Happy coding! 🚀**
