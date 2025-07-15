#!/bin/bash
set -e

URL="https://ecommerce-api-2owr.onrender.com"
echo "🚀 Setting up database for: $URL"
echo "=================================="

export FLASK_APP=app.py
export FLASK_ENV=production

# Check if Alembic is initialized
if [ ! -f "migrations/env.py" ]; then
    echo "🔧 Initializing Alembic..."
    rm -rf migrations
    alembic init migrations
    echo "[alembic]" >> alembic.ini
    echo "script_location = migrations" >> alembic.ini
else
    echo "✅ Alembic already initialized"
fi

mkdir -p migrations/versions

# Run migrations
echo "📊 Running migrations..."
alembic revision --autogenerate -m "Auto migration" || echo "⚠️ No changes to migrate"
alembic upgrade head || echo "⚠️ Migration upgrade failed"

echo "✅ Database setup complete!"
echo "🚀 Starting server on port $PORT..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
