#!/bin/bash
# Clean deployment script for production

echo "🚀 Starting E-commerce API Deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
flask db upgrade

# Initialize sample data (optional)
echo "📊 Setting up sample data..."
python scripts/create_sample_data.py

echo "✅ Deployment complete!"
echo "🌐 Your API is ready at the configured URL"
