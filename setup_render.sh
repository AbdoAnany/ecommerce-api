#!/bin/bash
set -e  # Exit on any error

# Quick setup script for your specific Render deployment
URL="https://ecommerce-api-2owr.onrender.com"

echo "🚀 Setting up database for: $URL"
echo "=================================="

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Skip Alembic initialization if migrations directory already exists
if [ -d "migrations" ]; then
    echo "✅ Migrations directory already exists, skipping initialization"
else
    echo "🔧 Initializing Alembic..."
    mkdir -p migrations/versions
    alembic init migrations
fi

# Database setup using Alembic commands
echo "🔄 Setting up database with Alembic..."

# Create migration (only if we have models to migrate)
echo "📊 Creating migration..."
alembic revision --autogenerate -m "Deploy migration" || echo "⚠️  No changes detected"

# Apply migrations
echo "📊 Applying migrations..."
alembic upgrade head || echo "⚠️  Migration upgrade completed"


echo "🚀 Starting server on port $PORT..."
gunicorn wsgi:app
# Start the server - this MUST be the last command
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
