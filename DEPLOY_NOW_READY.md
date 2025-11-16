# READY TO DEPLOY - Follow These Exact Steps

## YOUR CODE IS NOW ON GITHUB!

**Repository**: https://github.com/Phantom-bronze/UserModule

All your code, including PWA mobile features and Railway deployment files, has been pushed to GitHub.

---

## DEPLOY TO RAILWAY IN 5 STEPS (20 minutes)

### STEP 1: Login to Railway (2 minutes)

1. Go to: https://railway.app
2. Click "Login"
3. Choose "Login with GitHub"
4. Authorize Railway
5. You get $5 FREE credit per month!

---

### STEP 2: Create New Project (2 minutes)

1. Click "New Project" button
2. Select "Deploy from GitHub repo"
3. Find and click: **Phantom-bronze/UserModule**
4. Click "Deploy Now"

Railway will start building automatically. This takes about 2-3 minutes.

---

### STEP 3: Add PostgreSQL Database (1 minute)

While your app is building:

1. In your Railway project, click the **"+ New"** button
2. Select "Database"
3. Choose "Add PostgreSQL"
4. Wait ~30 seconds

Railway automatically connects the database to your app!

---

### STEP 4: Set Environment Variables (5 minutes)

**THIS IS THE MOST IMPORTANT STEP!**

1. Click on your **web service** (not the database)
2. Go to "Variables" tab
3. Click "Raw Editor" button
4. **Copy and paste this ENTIRE configuration**:

```env
APP_ENV=production
APP_NAME=Simple Digital Signage
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0

SECRET_KEY=b5d92fc995c1c2c9b2ff2fb0cb122f937d0ead85827bc3950b27d88beb50d1b8
ENCRYPTION_KEY=a0db766fc7f4fec40a0e8f14e627260e9664b9b60bb2cd4b88c9524dd847151d
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
INVITATION_TOKEN_EXPIRE_HOURS=72

GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE
GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile

CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True

LOG_LEVEL=INFO
LOG_FORMAT=json
```

5. **IMPORTANT**: Replace these two values:
   - `YOUR_GOOGLE_CLIENT_ID_HERE` with your actual Google Client ID
   - `YOUR_GOOGLE_CLIENT_SECRET_HERE` with your actual Google Client Secret

6. Click "Save"

---

### STEP 5: Get Your Domain & Update Google OAuth (10 minutes)

#### 5A: Generate Railway Domain (1 minute)

1. In your service, click "Settings" tab
2. Scroll to "Networking" section
3. Click "Generate Domain"
4. **Copy your domain** (looks like: `your-app-name.up.railway.app`)

**WRITE IT DOWN**: _______________________________________

#### 5B: Update Google OAuth (4 minutes)

1. Go to: https://console.cloud.google.com
2. Navigate to: **APIs & Services → Credentials**
3. Click on your **OAuth 2.0 Client ID**
4. Under "Authorized redirect URIs", click **"+ ADD URI"**
5. Add this (replace with YOUR Railway domain):
   ```
   https://YOUR-RAILWAY-DOMAIN/api/v1/auth/google/callback
   ```
   Example: `https://usermodule-production.up.railway.app/api/v1/auth/google/callback`
6. Click "Save"

#### 5C: Add Redirect URI to Railway (2 minutes)

Back in Railway:

1. Go to "Variables" tab
2. Click "Raw Editor"
3. Add this line (replace with YOUR Railway domain):
   ```env
   GOOGLE_REDIRECT_URI=https://YOUR-RAILWAY-DOMAIN/api/v1/auth/google/callback
   ```
4. Click "Save"

Railway will automatically redeploy (takes ~2 minutes).

---

## STEP 6: TEST YOUR APP! (3 minutes)

Visit these URLs (replace YOUR-RAILWAY-DOMAIN):

### Main App
```
https://YOUR-RAILWAY-DOMAIN/
```
You should see the login page!

### Health Check
```
https://YOUR-RAILWAY-DOMAIN/api/v1/health
```
Should return: `{"status":"healthy",...}`

### API Documentation
```
https://YOUR-RAILWAY-DOMAIN/api/docs
```
Interactive API documentation

### Test Login
1. Click "Sign in with Google"
2. Should redirect to Google
3. Login and authorize
4. Should redirect back to dashboard

---

## YOU'RE DONE!

Your app is now LIVE and accessible worldwide at:
**https://YOUR-RAILWAY-DOMAIN**

### What You Have Now:

- Web app accessible from any device
- Google OAuth login working
- PostgreSQL database
- Automatic HTTPS security
- PWA ready for mobile installation
- All user management features working

---

## INSTALL AS MOBILE APP

### On Android (Chrome):
1. Open your Railway URL on phone
2. Chrome shows "Install" prompt
3. Tap "Install"
4. App appears on home screen!

### On iOS (Safari):
1. Open your Railway URL on phone
2. Tap Share button
3. Tap "Add to Home Screen"
4. Done!

---

## TROUBLESHOOTING

### If Deployment Fails:

1. **Check Logs**:
   - Railway Dashboard → Your Service → Deployments → View Logs
   - Look for error messages

2. **Verify Environment Variables**:
   - Make sure all variables are set
   - Check GOOGLE_CLIENT_ID and SECRET are correct
   - Verify SECRET_KEY and ENCRYPTION_KEY are set

3. **Database Connection**:
   - Make sure PostgreSQL is in the same project
   - Railway auto-provides DATABASE_URL

### If Google Login Doesn't Work:

1. Verify redirect URI matches exactly (including `/api/v1/auth/google/callback`)
2. Check GOOGLE_CLIENT_ID is correct
3. Check GOOGLE_CLIENT_SECRET is correct
4. Make sure you saved changes in Google Console

### If App Doesn't Load:

1. Wait 2-3 minutes for initial deployment
2. Check deployment status in Railway
3. View logs for errors
4. Make sure PORT is not set (Railway sets it automatically)

---

## DON'T HAVE GOOGLE OAUTH CREDENTIALS?

### Get Them in 5 Minutes:

1. Go to: https://console.cloud.google.com
2. Create a new project (or select existing)
3. Go to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth client ID"
5. Choose "Web application"
6. Add name: "User Management App"
7. Under "Authorized redirect URIs", add:
   - `http://localhost:8000/api/v1/auth/google/callback` (for local testing)
   - `https://YOUR-RAILWAY-DOMAIN/api/v1/auth/google/callback` (for production)
8. Click "Create"
9. Copy Client ID and Client Secret

---

## SUMMARY

**Time**: 20 minutes total
**Cost**: FREE ($5/month credit included)
**Result**: Live web app + mobile PWA

**Your GitHub**: https://github.com/Phantom-bronze/UserModule
**Your Railway**: https://railway.app (login to see your project)

---

## NEXT STEPS AFTER DEPLOYMENT

1. Login as first user (becomes Super Admin automatically)
2. Create your company
3. Add users through the "+ Add User" button
4. Share your Railway URL with users
5. Test mobile installation on Android/iOS

---

## KEEP FREE TIER ACTIVE

Railway Free Tier:
- $5/month credit
- App sleeps after 30 minutes of inactivity
- Wakes up in ~5 seconds when accessed
- Perfect for small teams (< 100 users)

To keep app awake 24/7 (optional):
- Use UptimeRobot: https://uptimerobot.com (free)
- Ping your health endpoint every 5 minutes
- URL to ping: `https://YOUR-RAILWAY-DOMAIN/api/v1/health`

---

## NEED HELP?

**Railway Docs**: https://docs.railway.app
**Railway Discord**: https://discord.gg/railway

**Other Deployment Guides in This Repo**:
- `DEPLOY_HELP.md` - Troubleshooting guide
- `RAILWAY_QUICK_CHECKLIST.txt` - Quick checklist
- `DEPLOYMENT_GUIDE.md` - Alternative platforms (Render, Heroku)

---

**EVERYTHING IS READY! Just follow the 5 steps above.**

**Good luck!** 🚀
