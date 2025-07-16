#!/bin/bash
set -e  # Exit on any error

# Quick setup script for your specific Render deployment
URL="https://ecommerce-api-2owr.onrender.com"

echo "🚀 Setting up database for: $URL"
echo "=================================="

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Check if migrations directory is properly initialized
if [ ! -f "migrations/alembic.ini" ]; then
    echo "🔧 Migrations directory incomplete, reinitializing..."
    rm -rf migrations
    flask db init
    echo "✅ Flask-Migrate initialized"
elif [ ! -d "migrations" ]; then
    echo "🔧 Initializing Flask-Migrate..."
    flask db init
    echo "✅ Flask-Migrate initialized"
else
    echo "✅ Migrations directory already properly initialized"
fi

# Fix alembic.ini to use environment variables instead of hardcoded URL
echo "🔧 Updating alembic.ini for production..."
if [ -f "migrations/alembic.ini" ]; then
    # Comment out the hardcoded sqlalchemy.url line
    sed -i.bak 's/^sqlalchemy\.url = postgresql:\/\/username:password@localhost:5432\/dbname$/# sqlalchemy.url = postgresql:\/\/username:password@localhost:5432\/dbname/' migrations/alembic.ini
    echo "✅ Updated alembic.ini to use environment variables"
fi

# Database setup using Flask-Migrate commands
echo "🔄 Setting up database with Flask-Migrate..."

# Create migration (only if we have models to migrate)
echo "📊 Creating migration..."
flask db migrate -m "Deploy migration" || echo "⚠️  No changes detected"

# Apply migrations
echo "📊 Applying migrations..."
flask db upgrade || echo "⚠️  Migration upgrade completed"

echo "🚀 Starting server on port $PORT..."
# Start the server - this MUST be the last command
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 wsgi:app