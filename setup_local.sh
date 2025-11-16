#!/bin/bash
# ============================================================
# Local Development Setup - Linux/Mac
# ============================================================

set -e

echo ""
echo "========================================================"
echo "🚀 Simple Digital Signage - Local Setup (Linux/Mac)"
echo "========================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed!"
    echo "Please install Python 3.8+ from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python is installed"
python3 --version
echo ""

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL command-line tools not found in PATH"
    echo "Make sure PostgreSQL is installed and running"
    echo ""
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
else
    echo "✅ PostgreSQL is installed"
    psql --version
fi
echo ""

# Create virtual environment
if [ -d ".venv" ]; then
    echo "✅ Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please configure your .env file before proceeding."
    echo "See .env.example for reference."
    exit 1
fi
echo "✅ .env file exists"
echo ""

# Check PostgreSQL connection
echo "🔍 Checking database connection..."
python -c "from app.database import check_db_connection; exit(0 if check_db_connection() else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to database!"
    echo ""
    echo "💡 Please check:"
    echo "   1. PostgreSQL is running"
    echo "   2. Database exists: digital_signage"
    echo "   3. DATABASE_URL in .env is correct"
    echo ""
    echo "To create database, run:"
    echo "   createdb digital_signage"
    echo "   or: psql -U postgres -c \"CREATE DATABASE digital_signage;\""
    echo ""
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
else
    echo "✅ Database connection successful"
fi
echo ""

# Ask about database initialization
echo "========================================================"
echo "🗄️  Database Initialization"
echo "========================================================"
echo ""
echo "Do you want to initialize the database?"
echo ""
echo "Options:"
echo "  1. Create tables only"
echo "  2. Create tables + sample data (recommended for testing)"
echo "  3. Reset database (WARNING: deletes all data)"
echo "  4. Skip (database already initialized)"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📋 Creating database tables..."
        python init_local_db.py
        ;;
    2)
        echo ""
        echo "📋 Creating database tables with sample data..."
        python init_local_db.py --sample-data
        ;;
    3)
        echo ""
        echo "⚠️  WARNING: This will delete ALL existing data!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            python init_local_db.py --reset --sample-data
        else
            echo "❌ Cancelled"
        fi
        ;;
    *)
        echo "⏭️  Skipping database initialization"
        ;;
esac

echo ""
echo "========================================================"
echo "✅ Local Setup Complete!"
echo "========================================================"
echo ""
echo "🚀 To start the application, run:"
echo "   ./run_local.sh"
echo ""
echo "Or manually:"
echo "   source .venv/bin/activate"
echo "   python main.py"
echo ""
echo "🌐 Then open:"
echo "   Frontend: file://$(pwd)/frontend/index.html"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo ""
