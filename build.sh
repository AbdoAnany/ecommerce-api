#!/bin/bash

# Render Build Script - runs during deployment
echo "🚀 Starting Render build process..."

# Ensure we're in the correct working directory
echo "📁 Current directory: $(pwd)"

# Check Python version
echo "🐍 Python version:"
python --version

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Optional: Run migrations or database setup if needed
# echo "🔁 Running database migrations..."
# flask db upgrade

echo "✅ Build process completed successfully!"
echo "ℹ️  After deployment, call POST /setup/init-db to initialize the database"