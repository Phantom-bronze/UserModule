# 🧪 Complete Testing Guide - Simple Digital Signage

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Testing the UI](#testing-the-ui)
3. [Testing the API](#testing-the-api)
4. [Common Test Scenarios](#common-test-scenarios)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Access Points
- **Frontend UI:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs
- **API Root:** http://localhost:8000/api
- **Health Check:** http://localhost:8000/api/v1/health

---

## 🎨 Testing the UI

### Step 1: Open the Application
1. Open your browser
2. Navigate to: **http://localhost:8000**
3. You should see the login page with:
   - Simple Digital Signage logo (green checkmark)
   - "Sign in with Google" button
   - Manual token input option

### Step 2: UI Components to Check

#### Login Page
- ✅ Logo displays correctly
- ✅ Google Sign-In button is styled properly
- ✅ Manual token input field is visible
- ✅ Help text is shown at the bottom
- ✅ Page is centered and responsive

#### What You'll See:
```
┌─────────────────────────────────────┐
│        [Green Logo Icon]            │
│   Simple Digital Signage            │
│                                     │
│   [  Sign in with Google  ]         │
│                                     │
│         ── OR ──                    │
│                                     │
│   [Paste access token here]         │
│   [     Sign In     ]               │
│                                     │
│   First time? The first user...     │
└─────────────────────────────────────┘
```

---

## 🔧 Testing the API

### Method 1: Using Swagger UI (Easiest)

1. **Open API Documentation**
   - Go to: http://localhost:8000/api/docs
   - You'll see all available endpoints

2. **Test Health Check**
   - Click on `GET /api/v1/health`
   - Click "Try it out"
   - Click "Execute"
   - You should see:
     ```json
     {
       "status": "healthy",
       "service": "Simple Digital Signage",
       "version": "1.0.0"
     }
     ```

3. **Explore Available Endpoints**
   - **Authentication** (`/api/v1/auth/*`)
     - Google login
     - Token refresh
     - Current user info

   - **Companies** (`/api/v1/companies/*`)
     - List companies
     - Create company
     - Get company details

   - **Users** (`/api/v1/users/*`)
     - List users
     - Get user details
     - Update user

   - **Devices** (`/api/v1/devices/*`)
     - List devices
     - Link device
     - Delete device

   - **Invitations** (`/api/v1/invitations/*`)
     - Send invitation
     - List invitations
     - Cancel invitation

### Method 2: Using curl Commands

#### Test Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Simple Digital Signage",
  "version": "1.0.0"
}
```

#### Get API Info
```bash
curl http://localhost:8000/api
```

Expected response:
```json
{
  "name": "Simple Digital Signage",
  "version": "1.0.0",
  "environment": "development",
  "docs": "/api/docs",
  "status": "running"
}
```

---

## 📝 Common Test Scenarios

### Scenario 1: Testing Without Authentication

**Available Endpoints (No Auth Required):**
1. Health Check: `GET /api/v1/health`
2. API Info: `GET /api`
3. API Documentation: `GET /api/docs`

**Test Steps:**
```bash
# 1. Check if server is running
curl http://localhost:8000/api/v1/health

# 2. Get API information
curl http://localhost:8000/api

# 3. Open browser to see UI
# Navigate to: http://localhost:8000
```

### Scenario 2: Testing Google OAuth Flow

**Prerequisites:**
- Google OAuth credentials configured in `.env`
- Valid `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

**Test Steps:**
1. Open: http://localhost:8000
2. Click "Sign in with Google"
3. You'll be redirected to Google login
4. After successful login, you'll be redirected back
5. You should see the dashboard

### Scenario 3: Testing Manual Token Login

**For Development/Testing:**
1. You would need to obtain a token from the `/api/v1/auth/google/callback` endpoint
2. Paste the token in the manual input field
3. Click "Sign In"

---

## 🔍 Testing the Database

### Check Database Connection
```bash
# The health endpoint confirms DB is working
curl http://localhost:8000/api/v1/health
```

### Verify Tables Were Created
The application automatically creates these tables on startup:
- `users` - User accounts
- `companies` - Organizations
- `devices` - Smart TV devices
- `invitations` - User invitations
- `audit_logs` - Activity logs

---

## 🎯 UI Navigation Testing

Once logged in, test the navigation:

### Sidebar Navigation
1. **📊 Overview** - Dashboard overview
2. **🏢 Companies** - Company management
3. **👥 Users** - User management
4. **📺 Devices** - Device management
5. **✉️ Invitations** - Invitation management

### User Profile Section
- Located at bottom of sidebar
- Shows user avatar, name, and role
- Logout button

### Test Interactions:
1. Click each navigation item
2. Verify the page title changes
3. Verify content area updates
4. Click refresh button (🔄)
5. Click logout button

---

## ⚠️ Troubleshooting

### Issue: Can't See UI Design

**Solution:**
1. Make sure you're accessing: http://localhost:8000 (NOT http://localhost:8000/api)
2. Clear browser cache (Ctrl + F5)
3. Check browser console for errors (F12)

### Issue: "Cannot connect to database"

**Solution:**
1. Verify PostgreSQL is running
2. Check DATABASE_URL in `.env` file
3. Verify database exists: `digital_signage`
4. Check credentials match your PostgreSQL setup

### Issue: Google Sign-In Not Working

**Expected Behavior:**
- Google OAuth requires proper credentials
- Without valid `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, this won't work
- This is normal for development setup

**Solution:**
- Use the API documentation to test backend functionality
- Or configure Google OAuth credentials in `.env`

### Issue: Static Files Not Loading (CSS/JS)

**Solution:**
1. Check browser console for 404 errors
2. Verify files exist in `frontend/` directory
3. Restart the application

---

## ✅ Success Checklist

### Backend
- [ ] Application starts without errors
- [ ] Health check returns "healthy"
- [ ] API documentation accessible at /api/docs
- [ ] Database connection successful
- [ ] All tables created automatically

### Frontend
- [ ] UI loads at http://localhost:8000
- [ ] Login page displays correctly
- [ ] CSS styling is applied (green theme)
- [ ] Logo and icons visible
- [ ] Buttons are clickable

### Navigation
- [ ] Navigation items respond to clicks
- [ ] Page content updates when switching pages
- [ ] Refresh button works
- [ ] User profile section visible

---

## 🎓 Next Steps

### For Full Testing:
1. **Configure Google OAuth:**
   - Get credentials from Google Cloud Console
   - Update `.env` with `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - Test complete login flow

2. **Test Company Management:**
   - Create a company
   - View company details
   - Update company info

3. **Test User Management:**
   - Invite users
   - Assign roles
   - Deactivate/activate users

4. **Test Device Management:**
   - Generate device pairing codes
   - Link devices
   - View device status

---

## 📊 Performance Testing

### Check Response Times
Look at the `X-Process-Time` header in responses:
```bash
curl -I http://localhost:8000/api/v1/health
```

You should see:
```
X-Process-Time: 0.001234 (sub-second response)
```

### Monitor Logs
The application logs show:
- Request method and path
- Response status
- Processing time
- Database queries

---

## 🔐 Security Notes

### Current State (Development):
- ✅ Encryption key validation on startup
- ✅ CORS configured for localhost
- ✅ JWT token-based authentication
- ✅ Password hashing with bcrypt
- ⚠️ Debug mode enabled (API docs accessible)
- ⚠️ Default secret keys (change for production)

### For Production:
1. Change `SECRET_KEY` and `ENCRYPTION_KEY` in `.env`
2. Set `DEBUG=False`
3. Configure proper CORS origins
4. Use HTTPS
5. Set up proper Google OAuth redirect URIs

---

## 💡 Tips

1. **Use API Documentation First:**
   - Easiest way to test without setting up OAuth
   - Interactive and shows all available endpoints
   - No additional tools needed

2. **Monitor Application Logs:**
   - Watch the terminal where the app is running
   - See all requests in real-time
   - Helps debug issues

3. **Browser Developer Tools:**
   - Press F12 to open
   - Check Network tab for API calls
   - Check Console for JavaScript errors

4. **Test Incrementally:**
   - Start with health check
   - Test each endpoint group
   - Then test full user flows

---

## 🎉 Happy Testing!

If you encounter any issues:
1. Check this guide first
2. Review application logs
3. Verify database connection
4. Check browser console for errors
5. Restart the application if needed

The application is now fully functional and ready for testing!
