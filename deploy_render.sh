#!/bin/bash

# 🎨 Render Deployment Script

echo "🎨 Starting Render deployment setup..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📋 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
fi

# Generate secure keys
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "🔑 Generated secure keys:"
echo "SECRET_KEY: $SECRET_KEY"
echo "JWT_SECRET_KEY: $JWT_SECRET_KEY"

echo ""
echo "🚀 Render Deployment Instructions:"
echo "=================================="
echo ""
echo "1. Go to https://render.com and sign up with GitHub"
echo "2. Click 'New' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Configure the service:"
echo "   - Name: ecommerce-api"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn wsgi:app"
echo "   - Plan: Free"
echo ""
echo "5. Add Environment Variables:"
echo "   FLASK_ENV=production"
echo "   DEBUG=False"
echo "   SECRET_KEY=$SECRET_KEY"
echo "   JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo ""
echo "6. Create PostgreSQL Database:"
echo "   - In Render dashboard, click 'New' → 'PostgreSQL'"
echo "   - Name: ecommerce-db"
echo "   - Plan: Free"
echo "   - Copy the 'Internal Database URL'"
echo "   - Add to your web service as: DATABASE_URL=<internal-url>"
echo ""
echo "7. Deploy and Setup:"
echo "   - Click 'Deploy'"
echo "   - Once deployed, go to Shell tab"
echo "   - Run: python deploy.py"
echo "   - Run: python create_sample_data.py"
echo ""
echo "✅ Your API will be available at: https://ecommerce-api.onrender.com"
echo ""
echo "📊 Test endpoints:"
echo "   - Health: https://ecommerce-api.onrender.com/ping"
echo "   - API Info: https://ecommerce-api.onrender.com/api/v1"
echo ""
echo "🔗 Update your Postman collection base_url to your Render URL!"

# Save keys to a file for reference
echo "# Render Environment Variables" > render_env_vars.txt
echo "FLASK_ENV=production" >> render_env_vars.txt
echo "DEBUG=False" >> render_env_vars.txt
echo "SECRET_KEY=$SECRET_KEY" >> render_env_vars.txt
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> render_env_vars.txt
echo "" >> render_env_vars.txt
echo "# Copy these to your Render service environment variables" >> render_env_vars.txt

echo "💾 Environment variables saved to: render_env_vars.txt"
