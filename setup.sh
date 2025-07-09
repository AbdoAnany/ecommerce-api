#!/bin/bash

# E-commerce API Setup Script

echo "🚀 Setting up E-commerce API Backend..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating environment file..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Initialize database
echo "🗄️ Initializing database..."
export FLASK_APP=app.py
flask db init 2>/dev/null || echo "Database already initialized"
flask db migrate -m "Initial migration" 2>/dev/null || echo "Migration already exists"
flask db upgrade

# Create sample data
echo "📊 Creating sample data..."
python create_sample_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔧 To start the development server:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 API will be available at: http://localhost:5000"
echo "📚 Health check: http://localhost:5000/ping"
echo "📋 API info: http://localhost:5000/api/v1"
echo ""
echo "👤 Test Users:"
echo "   Admin: admin@example.com / admin123"
echo "   Customer: customer@example.com / customer123"
echo ""
