#!/bin/bash

# 🚀 Quick Railway Deployment Script

echo "🚂 Starting Railway deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize project
echo "📦 Initializing Railway project..."
railway init

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Set environment variables
echo "⚙️ Setting environment variables..."
railway env set FLASK_ENV=production
railway env set DEBUG=False

# Generate secure keys if not provided
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "🔑 Generated SECRET_KEY: $SECRET_KEY"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "🔑 Generated JWT_SECRET_KEY: $JWT_SECRET_KEY"
fi

railway env set SECRET_KEY="$SECRET_KEY"
railway env set JWT_SECRET_KEY="$JWT_SECRET_KEY"

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment initiated! Check Railway dashboard for status."
echo "🔗 Once deployed, run: railway shell"
echo "📊 Then setup database: python deploy.py && python create_sample_data.py"
