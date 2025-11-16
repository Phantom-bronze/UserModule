# 🚂 Deploy to Railway - Complete Guide

## 🎯 Your GitHub Repository
**Repository**: https://github.com/Phantom-bronze/UserModule.git

---

## ✅ Step-by-Step Deployment

### Step 1: Create Railway Account (2 minutes)

1. **Go to**: https://railway.app
2. **Click**: "Start a New Project" or "Login"
3. **Choose**: "Login with GitHub"
4. **Authorize**: Railway to access your GitHub account
5. **Done!** You'll get **$5 FREE credit per month**

---

### Step 2: Create New Project (1 minute)

1. **Click**: "New Project" button (top right)
2. **Select**: "Deploy from GitHub repo"
3. **Find and select**: `Phantom-bronze/UserModule`
4. **Click**: "Deploy Now"

Railway will automatically:
- ✅ Detect it's a Python project
- ✅ Install dependencies from `requirements.txt`
- ✅ Start building your app

**Wait ~2-3 minutes for initial build**

---

### Step 3: Add PostgreSQL Database (1 minute)

While your app is building:

1. **In your Railway project**, click the **"+ New"** button
2. **Select**: "Database"
3. **Choose**: "Add PostgreSQL"
4. **Wait** ~30 seconds for database creation

**Railway automatically connects the database!** ✅

---

### Step 4: Configure Environment Variables (5 minutes)

This is the MOST IMPORTANT step!

1. **Click** on your **web service** (not the database)
2. **Go to**: "Variables" tab
3. **Click**: "Raw Editor" button
4. **Copy and paste** this template:

```env
# Application Settings
APP_ENV=production
APP_NAME=Simple Digital Signage
APP_VERSION=1.0.0
DEBUG=False

# Server Configuration
HOST=0.0.0.0

# Security Keys - GENERATE THESE!
SECRET_KEY=CHANGE_THIS_TO_RANDOM_64_CHAR_STRING
ENCRYPTION_KEY=CHANGE_THIS_TO_RANDOM_64_CHAR_STRING
ALGORITHM=HS256

# Token Settings
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
INVITATION_TOKEN_EXPIRE_HOURS=72

# Google OAuth - UPDATE THESE!
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile

# CORS Settings
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

5. **Click**: "Add" or "Save"

---

### Step 5: Generate Secure Keys (2 minutes)

**IMPORTANT**: You need to generate random keys for security!

**Option A: Using PowerShell/Command Prompt**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"
```

**Option B: Online Generator**
- Go to: https://randomkeygen.com/
- Use "CodeIgniter Encryption Keys" (256-bit)
- Copy two different keys

**Update these in Railway Variables:**
- Replace `SECRET_KEY=CHANGE_THIS...` with your generated key
- Replace `ENCRYPTION_KEY=CHANGE_THIS...` with your generated key

---

### Step 6: Generate Your Domain (1 minute)

1. **In your service**, click **"Settings"** tab
2. **Scroll down** to "Networking" section
3. **Click**: "Generate Domain"
4. **Copy your domain** - it will look like:
   ```
   your-app-name.up.railway.app
   ```

**This is your live app URL!** 🎉

---

### Step 7: Update Google OAuth Settings (3 minutes)

1. **Go to**: https://console.cloud.google.com
2. **Navigate to**: APIs & Services → Credentials
3. **Click** on your OAuth 2.0 Client ID
4. **Under "Authorized redirect URIs"**, click **"+ ADD URI"**
5. **Add this** (replace with your Railway domain):
   ```
   https://your-app-name.up.railway.app/api/v1/auth/google/callback
   ```
6. **Click**: "Save"

---

### Step 8: Update Railway with OAuth Redirect URI (1 minute)

Back in Railway:

1. **Go to**: "Variables" tab
2. **Click**: "Raw Editor"
3. **Add/Update** this line (replace with your Railway domain):
   ```env
   GOOGLE_REDIRECT_URI=https://your-app-name.up.railway.app/api/v1/auth/google/callback
   ```
4. **Click**: "Save"

Railway will automatically redeploy with new settings!

---

### Step 9: Wait for Deployment (2 minutes)

1. **Go to**: "Deployments" tab
2. **Watch** the build logs
3. **Wait** for "Success" status

You'll see:
- ✅ Installing dependencies
- ✅ Starting application
- ✅ Application running on port...

---

### Step 10: Test Your Deployed App! (2 minutes)

**Visit these URLs** (replace with your domain):

1. **Main App**:
   ```
   https://your-app-name.up.railway.app
   ```
   You should see the login page!

2. **Health Check**:
   ```
   https://your-app-name.up.railway.app/api/v1/health
   ```
   Should return: `{"status":"healthy",...}`

3. **API Documentation**:
   ```
   https://your-app-name.up.railway.app/api/docs
   ```
   Interactive API docs!

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Main page loads (login screen visible)
- [ ] Health endpoint returns "healthy"
- [ ] API docs page loads
- [ ] Google "Sign in" button works
- [ ] Can login with Google
- [ ] Database connection works
- [ ] Can create users (after login as super admin)

---

## 🎉 Success! Your App is Live!

**Share your app**: `https://your-app-name.up.railway.app`

**What works now:**
- ✅ Web app accessible worldwide
- ✅ Google OAuth login
- ✅ User management
- ✅ All features working
- ✅ PostgreSQL database
- ✅ Automatic HTTPS

---

## 📱 Next Step: Install as Mobile App

**On Android (Chrome):**
1. Open your Railway URL on phone
2. Chrome will show "Install" prompt
3. Tap "Install"
4. App appears on home screen!

**On iOS (Safari):**
1. Open your Railway URL
2. Tap Share → "Add to Home Screen"
3. Done!

---

## 🔧 Troubleshooting

### Issue: "Application Error"

**Solution**: Check deployment logs
1. Go to Railway dashboard
2. Click your service
3. "Deployments" tab
4. Click latest deployment
5. View logs for errors

**Common causes**:
- Missing environment variables
- DATABASE_URL not set (should be automatic)
- Google OAuth credentials incorrect

### Issue: "Cannot connect to database"

**Solution**:
- Make sure PostgreSQL database is added to project
- Check both services are in same project
- Railway auto-provides DATABASE_URL

### Issue: "Google login not working"

**Solution**:
- Verify GOOGLE_CLIENT_ID is correct
- Verify GOOGLE_CLIENT_SECRET is correct
- Check redirect URI matches exactly
- Make sure you saved changes in Google Console

### Issue: "Module not found" or "Package errors"

**Solution**:
- Check `requirements.txt` is in repository
- Verify all dependencies are listed
- Check Railway build logs for specific error

---

## 💡 Pro Tips

### View Real-time Logs:
1. Railway dashboard → Your service
2. "Deployments" tab → Click deployment
3. Logs appear in real-time

### Keep Free Tier Active:
- Railway gives $5/month free credit
- App sleeps after 30 mins inactivity
- Wakes in ~5 seconds when accessed

### Auto-Deploy on Git Push:
- Any push to GitHub automatically deploys
- Push changes → Wait ~2 mins → Live!

### Custom Domain (Optional):
1. Settings → Networking
2. "Custom Domain"
3. Add your domain
4. Update DNS records as shown

---

## 📊 What You Get FREE:

✅ **$5/month credit** (enough for development)
✅ **PostgreSQL database**
✅ **Automatic HTTPS**
✅ **Auto-deploy from GitHub**
✅ **Zero-downtime deployments**
✅ **Environment variables**
✅ **Build & deployment logs**

---

## 🎯 Summary

**Total Time**: ~20 minutes

**Steps**:
1. ✅ Login to Railway with GitHub
2. ✅ Deploy from repository
3. ✅ Add PostgreSQL
4. ✅ Set environment variables
5. ✅ Generate domain
6. ✅ Update Google OAuth
7. ✅ Test!

**Result**: Your app is LIVE at `https://your-app-name.up.railway.app`

---

## 📞 Need Help?

**Railway Documentation**: https://docs.railway.app
**Railway Discord**: https://discord.gg/railway
**Deployment Logs**: Railway Dashboard → Deployments

---

## 🚀 You're Ready!

1. Go to https://railway.app
2. Login with GitHub
3. Deploy from: `Phantom-bronze/UserModule`
4. Follow steps above
5. Your app will be live in ~20 minutes!

**Good luck!** 🎉
