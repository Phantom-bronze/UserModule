# Deployment Guide - Simple Digital Signage

Complete guide to deploy your application to the cloud and make it accessible from anywhere.

---

## 🎯 Overview

To make your app accessible on mobile devices, you need to:
1. Deploy the **backend** to a cloud service
2. Deploy the **frontend** (served by backend, so automatic)
3. Update configuration URLs
4. Update Google OAuth settings

---

## 🚀 Method 1: Railway (Recommended - Easiest)

Railway offers free hosting with PostgreSQL database included.

### Step 1: Prerequisites

- GitHub account
- Railway account (free): https://railway.app

### Step 2: Push Code to GitHub

```bash
# Navigate to your project
cd C:\Users\Ash\Downloads\UserModule\UserManagementModule

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for deployment"

# Create GitHub repository (on GitHub website)
# Then link it:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 3: Deploy on Railway

1. **Go to Railway**: https://railway.app
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Select your repository**
6. **Railway will auto-detect** it's a Python project

### Step 4: Add PostgreSQL Database

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Database will be created and connected automatically

### Step 5: Set Environment Variables

1. **Click on your service** (not database)
2. Go to **"Variables"** tab
3. Click **"Raw Editor"**
4. Paste your `.env` contents (except DATABASE_URL - Railway provides this):

```env
APP_ENV=production
APP_NAME=Simple Digital Signage
APP_VERSION=1.0.0
DEBUG=False

SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-encryption-key-here

GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile

CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True

HOST=0.0.0.0
PORT=$PORT
```

**Important**:
- Railway automatically provides `DATABASE_URL`
- Use `PORT=$PORT` (Railway assigns this)
- Set `DEBUG=False` for production

### Step 6: Configure Start Command

1. Go to **"Settings"** tab
2. Under **"Deploy"**, set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 7: Generate Domain

1. Go to **"Settings"** tab
2. Under **"Networking"**, click **"Generate Domain"**
3. Copy your domain (e.g., `your-app-name.up.railway.app`)

### Step 8: Update Google OAuth

1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Navigate to **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 Client ID
4. Add to **Authorized redirect URIs**:
   ```
   https://your-app-name.up.railway.app/api/v1/auth/google/callback
   ```
5. Click **Save**

### Step 9: Update Environment Variables

Back in Railway, update:
```env
GOOGLE_REDIRECT_URI=https://your-app-name.up.railway.app/api/v1/auth/google/callback
```

### Step 10: Deploy!

Railway will automatically deploy. Monitor the deployment in the **"Deployments"** tab.

Once deployed, your app will be live at: `https://your-app-name.up.railway.app`

---

## 🎨 Method 2: Render.com (Alternative Free Hosting)

### Step 1: Create Render Account

Go to: https://render.com and sign up

### Step 2: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - Name: `digital-signage-db`
   - Database: `digital_signage`
   - User: `postgres`
3. Click **"Create Database"**
4. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Fill in:
   - Name: `digital-signage-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

Click **"Advanced"** and add:

```env
DATABASE_URL=<paste-internal-db-url-from-step-2>
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-app.onrender.com/api/v1/auth/google/callback
GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile
APP_ENV=production
DEBUG=False
PORT=$PORT
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy
3. Access at: `https://your-app.onrender.com`

### Step 6: Update Google OAuth

Same as Railway (Step 8 above), but use your Render URL.

---

## ☁️ Method 3: Heroku (Classic Option)

### Step 1: Install Heroku CLI

Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login to Heroku

```bash
heroku login
```

### Step 3: Create Heroku App

```bash
cd C:\Users\Ash\Downloads\UserModule\UserManagementModule
heroku create your-app-name
```

### Step 4: Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

### Step 5: Set Environment Variables

```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ENCRYPTION_KEY=your-encryption-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
heroku config:set GOOGLE_REDIRECT_URI=https://your-app-name.herokuapp.com/api/v1/auth/google/callback
heroku config:set GOOGLE_SCOPES="openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile"
heroku config:set APP_ENV=production
heroku config:set DEBUG=False
```

### Step 6: Create Procfile

Create `Procfile` in project root:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 7: Create runtime.txt

Create `runtime.txt`:

```
python-3.11.9
```

### Step 8: Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Step 9: Open App

```bash
heroku open
```

---

## 🔧 Post-Deployment Configuration

### Update Frontend Config

If your frontend config has hardcoded URLs, update `frontend/config.js`:

```javascript
const CONFIG = {
    // Use relative URLs (works automatically)
    API_BASE_URL: window.location.origin,
    // ... rest of config
};
```

### Initialize Database

Your database tables will be created automatically on first run (development mode).

For production, you should use migrations:

```bash
# SSH into your server or use Railway/Render console
python init_local_db.py
```

Or use Alembic migrations:

```bash
alembic upgrade head
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Home page loads: `https://your-app.com`
- [ ] API docs work: `https://your-app.com/api/docs`
- [ ] Health check: `https://your-app.com/api/v1/health`
- [ ] Google login works
- [ ] Database connection works
- [ ] Can create users
- [ ] PWA install prompt appears on mobile

---

## 🌐 Custom Domain (Optional)

### Using Railway:

1. Go to **Settings** → **Networking**
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Add DNS records as shown:
   - Type: `CNAME`
   - Name: `app`
   - Value: `your-app.up.railway.app`

### Using Render:

1. Go to **Settings** → **Custom Domains**
2. Click **"Add Custom Domain"**
3. Follow DNS instructions

---

## 📊 Monitoring & Logs

### Railway:
- Go to **Deployments** → **View Logs**
- Real-time logs of your application

### Render:
- Go to **Logs** tab
- Real-time and historical logs

### Heroku:
```bash
heroku logs --tail
```

---

## 💰 Cost Comparison

| Provider | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Railway** | $5 credit/month | $20/month minimum |
| **Render** | 750 hours/month | $7/month |
| **Heroku** | Eco dyno $5/month | $25/month |

**Recommendation**: Start with Railway (easiest) or Render (generous free tier).

---

## 🔐 Security Best Practices

### Production Settings:

```env
# ALWAYS set these in production:
APP_ENV=production
DEBUG=False

# Use strong secrets:
SECRET_KEY=<64-character-random-string>
ENCRYPTION_KEY=<64-character-random-string>

# Restrict CORS:
CORS_ORIGINS=https://your-app.com,https://www.your-app.com

# Use HTTPS only
HTTPS_ONLY=True
```

### Generate Secure Keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚨 Troubleshooting

### Issue: "Application Error" or 500 Error

**Check logs**:
- Railway: Deployments → View Logs
- Render: Logs tab
- Heroku: `heroku logs --tail`

**Common causes**:
- Missing environment variables
- Database connection failed
- Port configuration incorrect

### Issue: "Database connection failed"

**Solution**:
- Verify `DATABASE_URL` is set (auto-set by Railway/Render)
- Check database is running
- Ensure database connection string format is correct

### Issue: "Google OAuth not working"

**Solution**:
- Update redirect URI in Google Console
- Match exact URL (https vs http)
- Clear browser cookies

### Issue: "CORS Error"

**Solution**:
Update `CORS_ORIGINS` to include your domain:
```env
CORS_ORIGINS=https://your-app.com,http://localhost:8000
```

---

## 📱 Mobile Access

After deployment:

1. **Open on mobile browser**: `https://your-app.com`
2. **Chrome will show "Install" prompt**
3. **Tap Install** → App added to home screen
4. **Open like a native app**!

---

## 🎉 Success!

Your app is now deployed and accessible worldwide!

**Next Steps**:
1. ✅ Share the URL with users
2. ✅ Install PWA on mobile devices
3. ✅ (Optional) Create native Android app
4. ✅ (Optional) Publish to Play Store

**Your deployed app**: `https://your-app-name.up.railway.app`

---

## 📞 Support

If you encounter issues:

1. Check deployment logs
2. Verify environment variables
3. Test locally first
4. Review error messages
5. Check Google OAuth configuration

**Happy deploying!** 🚀
