#!/bin/bash

# Quick start script for development

echo "🚀 Starting E-commerce API Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
fi

# Set Flask environment
export FLASK_APP=app.py
export FLASK_ENV=development

echo "🔧 Environment: Development"
echo "🌐 Server will start on: http://localhost:5000"
echo "📚 API Documentation: http://localhost:5000/api/v1"
echo "🏥 Health Check: http://localhost:5000/ping"
echo ""
echo "👤 Test Users:"
echo "   Admin: admin@example.com / admin123"
echo "   Customer: customer@example.com / customer123"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the development server
python app.py
