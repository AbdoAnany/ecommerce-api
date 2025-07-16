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

# 3. Drop alembic_version table to remove reference to missing revision
echo "❌ Removing alembic_version table from database..."
psql "$DATABASE_URL" -c "DROP TABLE IF EXISTS alembic_version CASCADE;"
echo "✅ alembic_version table dropped"

# 4. Drop all tables from SQLAlchemy
echo "🗑 Dropping all existing tables via SQLAlchemy..."
flask shell <<EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.drop_all()
EOF
echo "✅ All tables dropped"

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

# 8. Verify basic database functionality
echo "🔍 Verifying database connection..."
python - <<END
from app import create_app
from flask_sqlalchemy import SQLAlchemy

app = create_app()
db = SQLAlchemy(app)

with app.app_context():
    try:
        db.session.execute("SELECT 1")
        print("✅ Database connection verified")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        exit(1)
END

# 9. Start the server
echo "🚀 Starting Gunicorn server on port ${PORT}"
exec gunicorn --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
