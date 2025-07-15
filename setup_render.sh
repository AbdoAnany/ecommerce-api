#!/bin/bash
set -e  # Exit on any error

# Quick setup script for your specific Render deployment
URL="https://ecommerce-api-2owr.onrender.com"

echo "🚀 Setting up database for: $URL"
echo "=================================="

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Create migrations directory
mkdir -p migrations/versions

# Initialize Alembic if not already done
if [ ! -f "alembic.ini" ]; then
    echo "🔧 Initializing Alembic..."
    # Remove migrations directory if it exists but is incomplete
    if [ -d "migrations" ] && [ ! -f "migrations/alembic.ini" ]; then
        echo "🗑️  Removing incomplete migrations directory..."
        rm -rf migrations
    fi
    alembic init migrations
else
    echo "✅ Alembic already initialized"
fi

# Database setup using Alembic commands
echo "🔄 Setting up database with Alembic..."

# Create migration
echo "📊 Creating migration..."
alembic revision --autogenerate -m "Initial migration" || echo "⚠️  Migration creation failed or no changes detected"

# Apply migrations
echo "📊 Applying migrations..."
alembic upgrade head || echo "⚠️  Migration upgrade failed"

# Set up initial data
echo "🏗️  Setting up initial data..."
python -c "
from app import create_app, db
from app.models import User, Category
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            email='admin@example.com',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created')
    
    # Create default categories if needed
    if Category.query.count() == 0:
        categories = [
            Category(name='Electronics', description='Electronic devices and gadgets'),
            Category(name='Clothing', description='Fashion and apparel'),
            Category(name='Books', description='Books and literature'),
            Category(name='Home & Garden', description='Home improvement and garden supplies')
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print('✅ Default categories created')
"

echo "✅ Database setup complete!"
echo "🚀 Starting server on port $PORT..."

# Start the server - this MUST be the last command
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 30 app:app
