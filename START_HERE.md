# 🚀 START HERE - Complete Setup Guide

**Welcome to Simple Digital Signage!**

This guide will get you from zero to running in about 15 minutes.

---

## ⚡ Super Quick Start (For Experienced Developers)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup PostgreSQL
createdb simple_digital_signage

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run the backend
python main.py

# 5. Open frontend
# Open frontend/index.html in your browser
```

---

## 📚 Detailed Guides

Choose based on your needs:

### 🆕 First Time Setup
**→ Read: `INSTALLATION_GUIDE.md`**
- Complete step-by-step installation
- PostgreSQL setup
- Google OAuth configuration
- Email setup
- All prerequisites

**Time**: ~15-20 minutes

### ⚡ Quick Setup
**→ Read: `QUICK_START.md`**
- 5-minute setup for experienced users
- Assumes you know the basics
- Fast track to get running

**Time**: ~5 minutes

### 🎨 Frontend Usage
**→ Read: `FRONTEND_GUIDE.md`**
- How to use the web interface
- All features explained
- Troubleshooting
- Customization guide

**Time**: ~10 minutes to read

### 📖 Full Documentation
**→ Read: `README.md`**
- Complete API reference
- Architecture overview
- Production deployment
- All features explained

**Time**: ~20 minutes to read

---

## 🎯 What Do You Want to Do?

### Option 1: "I just want to see it working"

1. **Install Python & PostgreSQL**
   - Python 3.8+: https://www.python.org/downloads/
   - PostgreSQL: https://www.postgresql.org/download/

2. **Run these commands:**
   ```bash
   cd "C:\Users\aggar\Desktop\akshit app"
   pip install -r requirements.txt
   python test_setup.py
   python main.py
   ```

3. **Open frontend:**
   - Open `frontend/index.html` in your browser
   - Click "Sign in with Google"

### Option 2: "I want to understand everything"

1. Read `INSTALLATION_GUIDE.md` (comprehensive)
2. Read `README.md` (documentation)
3. Read `FRONTEND_GUIDE.md` (UI guide)
4. Explore the code in `app/` directory

### Option 3: "I want to develop/customize"

1. Read `README.md` - understand architecture
2. Read code comments in:
   - `main.py` - application entry
   - `app/routers/` - API endpoints
   - `app/models/` - database models
3. Read `FRONTEND_GUIDE.md` - customize UI

---

## 📋 Checklist

Use this to track your setup:

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and running
- [ ] Git installed (optional)
- [ ] Text editor (VS Code, etc.)
- [ ] Google account (for OAuth)
- [ ] Gmail account (for email)

### Backend Setup
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL database created
- [ ] `.env` file created and configured
- [ ] SECRET_KEY and ENCRYPTION_KEY generated
- [ ] Google OAuth credentials obtained
- [ ] Email SMTP configured
- [ ] Verification script passed (`python test_setup.py`)
- [ ] Backend running (`python main.py`)

### Frontend Setup
- [ ] Opened `frontend/index.html` in browser
- [ ] Successfully logged in
- [ ] Can see dashboard
- [ ] All pages loading correctly

### First Steps
- [ ] Logged in (became Super Admin)
- [ ] Created first company
- [ ] Sent first invitation
- [ ] Explored all pages

---

## 🆘 Having Issues?

### Quick Fixes

**Backend won't start:**
```bash
# Check Python version
python --version  # Need 3.8+

# Check if PostgreSQL is running
# Windows: Check Services
# Mac: brew services list
# Linux: sudo systemctl status postgresql

# Verify database exists
psql -U postgres -l

# Check .env configuration
cat .env  # or: type .env (Windows)
```

**Frontend not connecting:**
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check browser console (F12) for errors

# Verify config.js has correct URL
# Should be: http://localhost:8000
```

**Google OAuth not working:**
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in `.env`
- Check redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
- Make sure Google+ API is enabled

### Where to Look

1. **Backend Issues**
   - Check terminal output where `python main.py` is running
   - Look for error messages in red
   - Read `INSTALLATION_GUIDE.md` → "Common Issues"

2. **Frontend Issues**
   - Open browser console: F12 → Console tab
   - Look for errors in red
   - Read `FRONTEND_GUIDE.md` → "Troubleshooting"

3. **Database Issues**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in `.env`
   - Try: `psql -U postgres simple_digital_signage`

---

## 📁 Project Structure

```
akshit app/
│
├── 📄 START_HERE.md          ← You are here!
├── 📄 INSTALLATION_GUIDE.md  ← Detailed setup
├── 📄 QUICK_START.md         ← 5-min setup
├── 📄 README.md              ← Full docs
├── 📄 FRONTEND_GUIDE.md      ← UI guide
├── 📄 DATABASE_SCHEMA.md     ← DB schema
│
├── 📄 main.py                ← Backend entry point
├── 📄 requirements.txt       ← Python packages
├── 📄 .env.example           ← Config template
├── 📄 test_setup.py          ← Verification script
│
├── 📁 app/                   ← Backend code
│   ├── 📁 routers/           ← API endpoints
│   ├── 📁 models/            ← Database models
│   ├── 📁 schemas/           ← Validation schemas
│   └── 📁 utils/             ← Helper functions
│
└── 📁 frontend/              ← Web interface
    ├── 📄 index.html         ← Main page
    ├── 📄 styles.css         ← Styling
    ├── 📄 config.js          ← Configuration
    ├── 📄 api.js             ← API client
    └── 📄 app.js             ← Application logic
```

---

## 🎓 Learning Path

### Day 1: Get It Running (1-2 hours)
1. ✅ Follow `INSTALLATION_GUIDE.md`
2. ✅ Get backend running
3. ✅ Open frontend
4. ✅ Login and explore

### Day 2: Understand the System (2-3 hours)
1. ✅ Read `README.md`
2. ✅ Read `DATABASE_SCHEMA.md`
3. ✅ Explore API docs: http://localhost:8000/api/docs
4. ✅ Try API endpoints

### Day 3: Customize (2-4 hours)
1. ✅ Read `FRONTEND_GUIDE.md`
2. ✅ Modify frontend colors
3. ✅ Add custom pages
4. ✅ Explore backend code

### Week 2: Build Features
1. ✅ Add WebSocket support
2. ✅ Implement content management
3. ✅ Add analytics
4. ✅ Create mobile app

---

## 🔗 Important Links

### Local URLs
- **Frontend**: `file:///C:/Users/aggar/Desktop/akshit app/frontend/index.html`
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/api/v1/health

### External Resources
- **Python**: https://www.python.org/
- **PostgreSQL**: https://www.postgresql.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Google Cloud**: https://console.cloud.google.com/

### Documentation
- Backend API: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Database Schema: `DATABASE_SCHEMA.md`

---

## 💡 Tips & Tricks

### Development Workflow

```bash
# Terminal 1: Backend
cd "C:\Users\aggar\Desktop\akshit app"
venv\Scripts\activate
python main.py

# Terminal 2: Database (optional)
psql -U postgres simple_digital_signage

# Browser: Frontend + API Docs
# Tab 1: frontend/index.html
# Tab 2: http://localhost:8000/api/docs
```

### Quick Commands

```bash
# Start backend
python main.py

# Verify setup
python test_setup.py

# Access database
psql -U postgres simple_digital_signage

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Check health
curl http://localhost:8000/api/v1/health
```

### Keyboard Shortcuts

- `Ctrl+C` - Stop backend
- `F12` - Browser dev tools
- `Ctrl+Shift+R` - Hard refresh browser
- `Ctrl+\` - Exit Python shell

---

## 🎯 Next Steps

After getting everything running:

1. **Explore the API**
   - http://localhost:8000/api/docs
   - Try different endpoints
   - Understand the data flow

2. **Create Your Setup**
   - Create companies
   - Invite users
   - Link devices

3. **Customize**
   - Change frontend colors
   - Add custom pages
   - Modify API endpoints

4. **Deploy to Production**
   - Read README.md → "Production Deployment"
   - Set up proper hosting
   - Configure HTTPS
   - Add monitoring

---

## 📞 Need Help?

### Self-Help Resources
1. **Check documentation**
   - `INSTALLATION_GUIDE.md` - setup issues
   - `FRONTEND_GUIDE.md` - UI issues
   - `README.md` - general questions

2. **Check logs**
   - Backend: Terminal output
   - Frontend: Browser console (F12)
   - Database: PostgreSQL logs

3. **Verify setup**
   ```bash
   python test_setup.py
   ```

### Debug Checklist
- [ ] Backend is running
- [ ] Database is accessible
- [ ] .env is configured correctly
- [ ] All dependencies installed
- [ ] Browser console shows no errors
- [ ] API docs are accessible

---

## 🎉 You're All Set!

If you've made it here, you should have:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend accessible via browser
- ✅ Google OAuth configured
- ✅ Email sending working
- ✅ First Super Admin account created

**What's next?**
- Create your first company
- Invite team members
- Link devices
- Start managing content!

---

**Happy Building! 🚀**

*Simple Digital Signage - Making digital content management simple.*
