#!/bin/bash
set -e  # Exit immediately if any command fails

echo "🚀 Starting fresh database setup"
echo "==============================="

# 1. Clean up existing migrations
echo "🧹 Cleaning up old migrations..."
rm -rf migrations/
echo "✅ Old migrations removed"

# 2. Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production



# 5. Initialize fresh migrations
echo "🆕 Initializing new migrations..."
flask db init

# 6. Configure alembic to use DATABASE_URL from environment
echo "⚙️  Configuring database connection..."
sed -i.bak 's|sqlalchemy.url = .*|sqlalchemy.url = ${DATABASE_URL}|' migrations/alembic.ini
echo "✅ Database connection configured"

# 7. Create and apply initial migration
echo "🔄 Creating initial migration..."
flask db migrate -m "Initial migration after reset"

echo "🔼 Applying database migrations..."
flask db upgrade


# 9. Start the server
echo "🚀 Starting Gunicorn server on port ${PORT}"
exec gunicorn --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
