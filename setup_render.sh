#!/bin/bash

# Quick setup script for your specific Render deployment
URL="https://ecommerce-api-2owr.onrender.com"

echo "🚀 Setting up database for: $URL"
echo "=================================="

echo "⏳ Waiting for redeploy to complete..."
sleep 30

echo "🔍 Checking health..."
curl -s $URL/setup/health | python3 -m json.tool

echo -e "\n🔄 Initializing database..."
response=$(curl -s -X POST $URL/setup/init-db)
echo $response | python3 -m json.tool

echo -e "\n🧪 Testing products endpoint..."
curl -s $URL/api/v1/products | python3 -m json.tool
mkdir -p migrations/versions
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
echo -e "\n✅ Setup complete! Your API is ready at: $URL"
