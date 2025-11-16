@echo off
REM ============================================================
REM Run Application Locally - Windows
REM ============================================================

echo.
echo ========================================================
echo 🚀 Starting Simple Digital Signage (Local Mode)
echo ========================================================
echo.

REM Check if virtual environment exists
if not exist .venv (
    echo ❌ Virtual environment not found!
    echo Please run setup_local.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Check database connection
echo 🔍 Checking database connection...
python -c "from app.database import check_db_connection; exit(0 if check_db_connection() else 1)" 2>nul
if errorlevel 1 (
    echo ❌ Cannot connect to database!
    echo.
    echo Please make sure:
    echo   1. PostgreSQL is running
    echo   2. Database exists
    echo   3. DATABASE_URL in .env is correct
    echo.
    pause
    exit /b 1
)
echo ✅ Database connection OK
echo.

echo ========================================================
echo ✅ Application Starting!
echo ========================================================
echo.
echo 🌐 Access the application at:
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/api/docs
echo    Frontend: file:///%cd:\=/%/frontend/index.html
echo.
echo Press Ctrl+C to stop the server
echo ========================================================
echo.

REM Start the application
python main.py
