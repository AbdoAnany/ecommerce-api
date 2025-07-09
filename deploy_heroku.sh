#!/bin/bash

# 🚀 Quick Heroku Deployment Script

echo "🌟 Starting Heroku deployment..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install from https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Get app name from user
echo "📝 Enter your Heroku app name (must be unique):"
read -r APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name is required!"
    exit 1
fi

# Login to Heroku
echo "🔐 Logging into Heroku..."
heroku auth:login

# Create Heroku app
echo "📦 Creating Heroku app: $APP_NAME"
heroku create "$APP_NAME"

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:essential-0 -a "$APP_NAME"

# Generate secure keys
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo "🔑 Setting environment variables..."
heroku config:set FLASK_ENV=production -a "$APP_NAME"
heroku config:set DEBUG=False -a "$APP_NAME"
heroku config:set SECRET_KEY="$SECRET_KEY" -a "$APP_NAME"
heroku config:set JWT_SECRET_KEY="$JWT_SECRET_KEY" -a "$APP_NAME"

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📋 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Add Heroku remote
heroku git:remote -a "$APP_NAME"

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git push heroku main

# Setup database
echo "🗄️ Setting up database with sample data..."
heroku run python create_sample_data.py -a "$APP_NAME"

echo "✅ Deployment complete!"
echo "🔗 Your API is available at: https://$APP_NAME.herokuapp.com"
echo "📊 Test with: https://$APP_NAME.herokuapp.com/ping"
