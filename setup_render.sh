#!/bin/bash
set -e  # Exit on any error

URL="https://ecommerce-api-2owr.onrender.com"
echo "🚀 Setting up database for: $URL"
echo "=================================="

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Only initialize Alembic if not already initialized
if [ ! -f "migrations/env.py" ]; then
  echo "🔧 Initializing Alembic..."
  rm -rf migrations  # Clean up if there's an incomplete folder
  alembic init migrations
else
  echo "✅ Alembic already initialized"
fi

# Ensure versions folder exists
mkdir -p migrations/versions

# Create and apply migration
echo "📊 Running migrations..."
alembic revision --autogenerate -m "Auto migration" || echo "⚠️ No changes to migrate"
alembic upgrade head

echo "✅ Database setup complete!"
echo "🚀 Starting server on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
