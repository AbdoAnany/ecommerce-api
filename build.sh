#!/bin/bash

# Render Build Script - runs during deployment
echo "🚀 Starting Render build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build process completed successfully!"
echo "ℹ️  After deployment, call POST /setup/init-db to initialize the database"
