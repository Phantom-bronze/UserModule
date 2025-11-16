#!/bin/bash
# ============================================================
# Run Application Locally - Linux/Mac
# ============================================================

echo ""
echo "========================================================"
echo "🚀 Starting Simple Digital Signage (Local Mode)"
echo "========================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup_local.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Check database connection
echo "🔍 Checking database connection..."
python -c "from app.database import check_db_connection; exit(0 if check_db_connection() else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to database!"
    echo ""
    echo "Please make sure:"
    echo "  1. PostgreSQL is running"
    echo "  2. Database exists"
    echo "  3. DATABASE_URL in .env is correct"
    echo ""
    exit 1
fi
echo "✅ Database connection OK"
echo ""

echo "========================================================"
echo "✅ Application Starting!"
echo "========================================================"
echo ""
echo "🌐 Access the application at:"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo "   Frontend: file://$(pwd)/frontend/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================"
echo ""

# Start the application
python main.py
