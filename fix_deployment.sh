#!/bin/bash

# Emergency deployment fix for psycopg2 issues
echo "🚨 Emergency Deployment Fix - PostgreSQL Driver Issues"
echo "======================================================"

echo "🔍 Checking current requirements..."
if grep -q "psycopg2-binary" requirements.txt; then
    echo "✅ Using psycopg2-binary"
elif grep -q "psycopg\[binary\]" requirements.txt; then
    echo "⚠️  Using psycopg3 - this might cause issues"
elif grep -q "psycopg2" requirements.txt; then
    echo "⚠️  Using psycopg2 - this might need system libraries"
else
    echo "❌ No PostgreSQL driver found!"
fi

echo ""
echo "🔧 Available fixes:"
echo "1. Use psycopg2-binary (most compatible with Render Python 3.11)"
echo "2. Use psycopg3 with proper SQLAlchemy config"
echo "3. Create alternative requirements for different Python versions"

echo ""
echo "Applying Fix #1: Use psycopg2-binary..."

# Create a known working requirements.txt for Render
cat > requirements-render-fixed.txt << 'EOF'
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.1
Flask-Marshmallow==0.15.0
marshmallow-sqlalchemy==0.29.0
marshmallow==3.20.2
bcrypt==4.2.0
python-dotenv==1.0.1
Pillow==10.4.0
email-validator==2.2.0
python-dateutil==2.9.0
Werkzeug==3.0.3
PyMySQL==1.1.1
# Render-compatible PostgreSQL driver
psycopg2-binary==2.9.9
gunicorn==22.0.0
EOF

echo "✅ Created requirements-render-fixed.txt"

# Update main requirements.txt to match
cp requirements-render-fixed.txt requirements.txt
echo "✅ Updated requirements.txt with working packages"

echo ""
echo "📋 Next steps:"
echo "1. Commit and push these changes"
echo "2. Redeploy on Render"
echo "3. Monitor deployment logs"

echo ""
echo "🔄 Ready to commit and deploy?"
read -p "Press Enter to commit changes or Ctrl+C to cancel..."

# Commit the fix
git add requirements.txt requirements-render-fixed.txt
git commit -m "Fix: Use psycopg2-binary for Render Python 3.11 compatibility

- Reverted from psycopg3 to psycopg2-binary for better Render support
- psycopg2-binary includes pre-compiled binaries and doesn't need system libs
- Added enhanced error handling in wsgi.py
- Created requirements-render-fixed.txt as backup"

echo "✅ Changes committed. Pushing to GitHub..."
git push origin main

echo "🚀 Deployment fix pushed! Check Render dashboard for new deployment."
echo "📊 Monitor: https://dashboard.render.com"
