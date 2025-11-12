# Frontend User Interface Guide

Complete guide to using the Simple Digital Signage web interface.

## Quick Start

### Step 1: Make Sure Backend is Running

Before using the frontend, ensure your backend is running:

```bash
cd "C:\Users\aggar\Desktop\akshit app"
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Open the Frontend

Simply open the HTML file in your browser:

**Option 1: Double-click**
- Navigate to: `C:\Users\aggar\Desktop\akshit app\frontend\`
- Double-click `index.html`

**Option 2: Using Browser**
- Open your browser (Chrome, Firefox, Edge, Safari)
- Press `Ctrl+O` (Windows/Linux) or `Cmd+O` (Mac)
- Navigate to `frontend/index.html`
- Click "Open"

**Option 3: Direct URL**
```
file:///C:/Users/aggar/Desktop/akshit app/frontend/index.html
```

### Step 3: Login

You'll see two login options:

#### Option A: Google OAuth (Recommended)
1. Click "Sign in with Google" button
2. You'll be redirected to Google
3. Login with your Google account
4. Grant permissions
5. **Note**: Due to CORS, you may need to manually copy the token from the callback

#### Option B: Manual Token Entry
1. Get your access token from the API docs or terminal
2. Paste it in the "Paste access token here" field
3. Click "Sign In"

**How to get a token manually:**
1. Open API docs: http://localhost:8000/api/docs
2. Navigate to `GET /api/v1/auth/google/login`
3. Click "Try it out" → "Execute"
4. Copy the `auth_url` from response
5. Open that URL in browser → Login with Google
6. Copy the `access_token` from the response
7. Paste into frontend

---

## Frontend Features

### 1. Overview Page

**What you'll see:**
- System health status
- Database connection status
- Environment mode (development/production)
- API version
- Component status (API, Database, Encryption)

**Actions:**
- 🔄 Click refresh button to update data
- View real-time system status

### 2. Companies Page

**What you'll see:**
- List of all companies (Super Admin only)
- Company name, subdomain
- User count (current / max allowed)
- Device count (current / max allowed)
- Company status (Active/Inactive)

**Actions:**
- Create new company (button at top right)
- View company details
- Monitor usage limits

**Example Company:**
```
Name: Acme Corporation
Subdomain: acme
Users: 5 / 50
Devices: 12 / 100
Status: Active
```

### 3. Users Page

**What you'll see:**
- List of all users in your company
- User name, email
- Role (Super Admin, Admin, User)
- Account status (Active/Inactive)
- Last login date

**Actions:**
- View user details
- Check user activity
- Monitor team members

### 4. Devices Page

**What you'll see:**
- List of devices linked to your account
- Device name
- Online/Offline status
- Last seen timestamp
- Linked date

**Actions:**
- **Link New Device**: Click "+ Link Device"
  1. Get 4-digit code from your TV
  2. Enter code in popup
  3. Device gets linked instantly
- View device status
- Monitor device connectivity

### 5. Invitations Page

**What you'll see:**
- List of sent invitations
- Invitee email
- Role (Admin/User)
- Status (Pending/Accepted/Expired/Cancelled)
- Expiration date

**Actions:**
- Send new invitation (button at top right)
- View invitation status
- Track team growth

---

## Navigation

### Sidebar Menu

**📊 Overview** - System dashboard and health
**🏢 Companies** - Manage companies (Super Admin)
**👥 Users** - View and manage users
**📺 Devices** - Manage your TV devices
**✉️ Invitations** - Send and track invitations

### User Menu (Bottom of Sidebar)

- Shows your profile picture
- Displays your name
- Shows your role
- **Logout button** - Click to sign out

### Header Actions

- **🔄 Refresh** - Reload current page data
- Page title shows which section you're in

---

## Frontend Architecture

### File Structure

```
frontend/
├── index.html      # Main HTML file
├── styles.css      # All styles and design
├── config.js       # API configuration
├── api.js          # API client and methods
└── app.js          # Application logic and UI
```

### How It Works

1. **index.html**
   - Login page layout
   - Dashboard layout (sidebar + main content)
   - Toast notifications
   - Loading overlay

2. **styles.css**
   - Modern, clean design
   - Responsive layout
   - Color scheme and themes
   - Component styles

3. **config.js**
   - API base URL configuration
   - All API endpoint definitions
   - Storage keys for tokens

4. **api.js**
   - API client class
   - All API methods (get, post, put, delete)
   - Token management
   - Auto token refresh
   - Error handling

5. **app.js**
   - Application state management
   - Page loading and routing
   - Event handlers
   - UI rendering
   - Data fetching and display

### Data Flow

```
User Action
    ↓
Event Handler (app.js)
    ↓
API Call (api.js)
    ↓
Backend API (main.py)
    ↓
Database Query
    ↓
Response Back to Frontend
    ↓
UI Update (app.js)
    ↓
User Sees Result
```

---

## Customization

### Changing API URL

Edit `frontend/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://your-api-server:8000',  // Change this
    // ...
};
```

### Changing Colors

Edit `frontend/styles.css`:

```css
:root {
    --primary: #4CAF50;        /* Change to your brand color */
    --secondary: #2196F3;
    --danger: #f44336;
    /* ... */
}
```

### Adding New Pages

1. **Add navigation item** in `index.html`:
```html
<a href="#" class="nav-item" data-page="mypage">
    <span class="icon">🎨</span>
    <span>My Page</span>
</a>
```

2. **Add page loader** in `app.js`:
```javascript
case 'mypage':
    await loadMyPage(contentArea);
    break;
```

3. **Create page function**:
```javascript
async function loadMyPage(container) {
    const data = await api.getMyData();
    container.innerHTML = `
        <h2>My Custom Page</h2>
        <!-- Your HTML here -->
    `;
}
```

---

## Troubleshooting

### Issue 1: "Failed to fetch" Error

**Cause**: Backend not running or wrong URL

**Solution:**
1. Check backend is running:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
2. Verify API_BASE_URL in `config.js`
3. Check browser console for errors (F12)

### Issue 2: CORS Errors

**Cause**: Browser blocking requests to localhost

**Solution:**
1. Make sure `CORS_ORIGINS` in backend `.env` includes:
   ```bash
   CORS_ORIGINS=http://localhost:3000,file://
   ```
2. Restart backend
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue 3: "Invalid Token" Error

**Cause**: Token expired (30 minutes)

**Solution:**
1. Tokens expire after 30 minutes
2. Frontend automatically tries to refresh
3. If refresh fails, just login again
4. Use refresh token if you have it

### Issue 4: Data Not Loading

**Cause**: API error or permissions

**Solution:**
1. Open browser console (F12)
2. Check Network tab for failed requests
3. Verify you have correct role/permissions
4. Check backend logs for errors

### Issue 5: Layout Broken

**Cause**: CSS not loading

**Solution:**
1. Make sure all files are in same directory:
   - index.html
   - styles.css
   - config.js
   - api.js
   - app.js
2. Refresh page (Ctrl+F5)
3. Check browser console for 404 errors

---

## Browser Compatibility

### Supported Browsers

✅ **Chrome** 90+ (Recommended)
✅ **Firefox** 88+
✅ **Edge** 90+
✅ **Safari** 14+
❌ **Internet Explorer** (Not supported)

### Required Features

- ES6 JavaScript
- Fetch API
- LocalStorage
- CSS Grid
- Flexbox

---

## Security Considerations

### Token Storage

- Access tokens stored in **localStorage**
- Automatically cleared on logout
- Never share your tokens
- Tokens expire after 30 minutes

### Best Practices

1. **Always logout** when done
2. **Don't share** your access tokens
3. **Use HTTPS** in production
4. **Clear tokens** if compromised:
   ```javascript
   // Open browser console (F12) and run:
   localStorage.clear();
   ```

---

## Production Deployment

### Hosting the Frontend

**Option 1: Static Hosting**
- Upload to: Netlify, Vercel, GitHub Pages
- Configure API_BASE_URL to production URL
- Enable HTTPS

**Option 2: With Backend**
- Place frontend in `backend/static/` folder
- Serve via FastAPI:
  ```python
  app.mount("/", StaticFiles(directory="static"), name="static")
  ```

**Option 3: CDN**
- Upload to S3 + CloudFront
- Configure CORS properly
- Use production API URL

### Production Checklist

- [ ] Update `API_BASE_URL` to production URL
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Minify JavaScript and CSS
- [ ] Add error tracking (Sentry)
- [ ] Add analytics (Google Analytics)
- [ ] Test on all browsers
- [ ] Enable caching headers
- [ ] Add loading states
- [ ] Add offline support (PWA)

---

## Advanced Features (Future)

### Planned Enhancements

1. **Real-time Updates**
   - WebSocket connection
   - Live device status
   - Instant notifications

2. **Content Management**
   - Upload images/videos
   - Create playlists
   - Schedule content

3. **Dashboard Analytics**
   - Usage charts
   - Device uptime graphs
   - User activity metrics

4. **Mobile Responsive**
   - Mobile-friendly layouts
   - Touch gestures
   - Native app feel

5. **Dark Mode**
   - Toggle light/dark theme
   - User preference saving
   - System theme detection

---

## Getting Help

### Debug Mode

Enable detailed logging:
1. Open browser console (F12)
2. Go to Console tab
3. All API calls and errors logged here

### Common Console Commands

```javascript
// Check if logged in
console.log(api.getAccessToken());

// Check current user
console.log(app.currentUser);

// Manually call API
api.checkHealth().then(console.log);

// Clear all data and logout
localStorage.clear();
location.reload();
```

### Support

- **Backend Logs**: Check terminal where backend is running
- **API Docs**: http://localhost:8000/api/docs
- **Browser Console**: F12 → Console tab
- **Network Tab**: F12 → Network tab (see API requests)

---

## Quick Reference

### Important URLs

- **Frontend**: `file:///path/to/frontend/index.html`
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Keyboard Shortcuts

- `F12` - Open browser dev tools
- `Ctrl+Shift+I` - Open inspector
- `Ctrl+Shift+C` - Element inspector
- `Ctrl+R` - Reload page
- `Ctrl+Shift+R` - Hard reload (clear cache)

### File Locations

- Frontend files: `C:\Users\aggar\Desktop\akshit app\frontend\`
- Backend files: `C:\Users\aggar\Desktop\akshit app\`
- Environment config: `C:\Users\aggar\Desktop\akshit app\.env`

---

**Enjoy your Simple Digital Signage Dashboard! 🚀**
