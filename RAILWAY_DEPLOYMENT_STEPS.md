# 🚂 Railway Deployment - Step-by-Step Guide

## ✅ Prerequisites Completed

I've already prepared these files for you:
- ✅ `Procfile` - Tells Railway how to start your app
- ✅ `railway.json` - Railway configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `.railwayignore` - Files to exclude from deployment

---

## 📋 Step-by-Step Instructions

### Step 1: Commit Your Changes to Git

Run these commands in your terminal:

```bash
cd C:\Users\Ash\Downloads\UserModule\UserManagementModule

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment - Add mobile app features"

# Push to GitHub
git push origin master
```

**If you get an error about uncommitted changes, that's OK - continue to next step.**

---

### Step 2: Create Railway Account

1. **Go to**: https://railway.app
2. **Click** "Login"
3. **Choose** "Login with GitHub"
4. **Authorize** Railway to access your GitHub

**You'll get $5 FREE credit per month!**

---

### Step 3: Create New Project

1. **Click** "New Project"
2. **Select** "Deploy from GitHub repo"
3. **Choose** your repository: `UserManagementModule`
4. **Click** "Deploy Now"

Railway will start building your app automatically!

---

### Step 4: Add PostgreSQL Database

1. **In your Railway project**, click **"New"** button
2. **Select** "Database"
3. **Choose** "Add PostgreSQL"
4. Wait for database to be created (takes ~30 seconds)

**Railway automatically connects the database to your app!**

---

### Step 5: Configure Environment Variables

1. **Click on your service** (not the database)
2. **Go to** "Variables" tab
3. **Click** "Raw Editor"
4. **Copy and paste** this (update the values):

```env
# Application Settings
APP_ENV=production
APP_NAME=Simple Digital Signage
APP_VERSION=1.0.0
DEBUG=False

# Server (Railway provides PORT automatically)
HOST=0.0.0.0

# Security Keys - GENERATE NEW ONES!
SECRET_KEY=REPLACE_WITH_YOUR_SECRET_KEY
ENCRYPTION_KEY=REPLACE_WITH_YOUR_ENCRYPTION_KEY
ALGORITHM=HS256

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
INVITATION_TOKEN_EXPIRE_HOURS=72

# Google OAuth - UPDATE THESE!
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile

# CORS
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

5. **Click** "Save"

---

### Step 6: Generate Secure Keys

Open PowerShell or Command Prompt and run:

```bash
# For SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# For ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

**Copy these values and update them in Railway Variables!**

---

### Step 7: Get Your Railway Domain

1. **In your service**, go to **"Settings"** tab
2. **Scroll to** "Networking" section
3. **Click** "Generate Domain"
4. **Copy your domain** (e.g., `your-app-name.up.railway.app`)

**This is your app URL!**

---

### Step 8: Update Google OAuth Settings

1. **Go to**: https://console.cloud.google.com
2. **Navigate to**: APIs & Services → Credentials
3. **Click** your OAuth 2.0 Client ID
4. **Add** to "Authorized redirect URIs":
   ```
   https://your-app-name.up.railway.app/api/v1/auth/google/callback
   ```
5. **Click** "Save"

---

### Step 9: Update Railway Environment Variable

Back in Railway Variables, add/update:

```env
GOOGLE_REDIRECT_URI=https://your-app-name.up.railway.app/api/v1/auth/google/callback
```

**Save and Railway will auto-redeploy!**

---

### Step 10: Verify Deployment

1. **Wait** for deployment to complete (~2 minutes)
2. **Click** on your domain or visit it in browser
3. **You should see** the login page!

**Test these URLs:**
- Main app: `https://your-app-name.up.railway.app`
- Health check: `https://your-app-name.up.railway.app/api/v1/health`
- API docs: `https://your-app-name.up.railway.app/api/docs`

---

## ✅ Post-Deployment Checklist

- [ ] App loads successfully
- [ ] Health check returns "healthy"
- [ ] Google login works
- [ ] Can create users
- [ ] Database connection works
- [ ] PWA install prompt appears on mobile

---

## 🔧 Troubleshooting

### Issue: "Application Error"

**Check deployment logs:**
1. Go to Railway project
2. Click on your service
3. Go to "Deployments" tab
4. Click on latest deployment
5. View logs for errors

**Common issues:**
- Missing environment variables
- Database not connected
- Python version mismatch

### Issue: "Database connection failed"

**Solution:**
- Railway auto-provides `DATABASE_URL`
- Make sure you added PostgreSQL database
- Check if service and database are in same project

### Issue: "Google OAuth not working"

**Solution:**
- Verify redirect URI matches exactly
- Check GOOGLE_CLIENT_ID and SECRET are correct
- Make sure scopes are set properly

---

## 📱 Test PWA Installation

After deployment:

1. **Open** `https://your-app-name.up.railway.app` on Android phone
2. **Chrome** will show "Install" prompt
3. **Tap** "Install"
4. **App** appears on home screen!

---

## 💡 Pro Tips

### Free Tier Limits:
- $5 credit per month (enough for small apps)
- App sleeps after 30 mins of inactivity
- Wakes up in ~5 seconds when accessed

### Keep App Awake (Optional):
Use a service like UptimeRobot to ping your app every 5 minutes:
- URL to ping: `https://your-app-name.up.railway.app/api/v1/health`
- Free on: https://uptimerobot.com

### View Logs:
- Real-time logs in "Deployments" → "View Logs"
- Useful for debugging

### Auto-Deploy:
- Railway auto-deploys when you push to GitHub
- Push changes → Wait ~2 mins → Changes live!

---

## 🎉 Success!

Your app is now deployed and accessible worldwide!

**Share this URL with users:**
`https://your-app-name.up.railway.app`

**Next steps:**
1. Generate app icons for PWA
2. Test on mobile devices
3. Share with users!

---

## 📞 Need Help?

**Railway Docs:** https://docs.railway.app
**Railway Discord:** https://discord.gg/railway
**Your deployment logs:** Railway Dashboard → Deployments → View Logs

---

**Your app is LIVE!** 🚀🎉
