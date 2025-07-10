#!/bin/bash

# Quick deployment completion script
echo "🎯 Complete Your Render Deployment"
echo "=================================="
echo ""

echo "📋 Step-by-step instructions:"
echo ""
echo "1️⃣  Get your Render URL:"
echo "   • Go to https://dashboard.render.com"
echo "   • Find your 'ecommerce-api' service"
echo "   • Copy the service URL"
echo ""

echo "2️⃣  Add environment variable in Render:"
echo "   • Go to service Environment tab"
echo "   • Add: ALLOW_DB_INIT = true"
echo "   • Save (this will redeploy)"
echo ""

echo "3️⃣  Initialize database (replace URL):"
echo "   curl -X POST https://YOUR-URL.onrender.com/setup/init-db"
echo ""

echo "4️⃣  Test your API:"
echo "   curl https://YOUR-URL.onrender.com/setup/health"
echo "   curl https://YOUR-URL.onrender.com/api/v1/products"
echo ""

echo "5️⃣  Run comprehensive test:"
echo "   python3 test_deployment.py https://YOUR-URL.onrender.com"
echo ""

echo "🎉 Expected result after database init:"
echo "   • Admin user: admin@example.com / admin123"
echo "   • 5 categories created"
echo "   • Sample products available"
echo "   • All API endpoints working"
echo ""

echo "🔗 Then access your admin panel at: YOUR-URL/admin"
echo ""

read -p "Press Enter when you have your Render URL ready..."
echo ""
echo "Enter your Render URL (e.g., https://ecommerce-api-abc123.onrender.com):"
read RENDER_URL

if [ ! -z "$RENDER_URL" ]; then
    echo ""
    echo "🧪 Testing your deployment at: $RENDER_URL"
    echo ""
    
    # Test health endpoint
    echo "1. Testing health endpoint..."
    curl -s "$RENDER_URL/setup/health" | python3 -m json.tool 2>/dev/null || echo "Health endpoint not yet ready"
    
    echo ""
    echo "2. Testing database initialization..."
    echo "   Running: curl -X POST $RENDER_URL/setup/init-db"
    echo ""
    
    curl -X POST "$RENDER_URL/setup/init-db" | python3 -m json.tool 2>/dev/null || echo "Database init endpoint response received"
    
    echo ""
    echo "3. Testing products endpoint..."
    curl -s "$RENDER_URL/api/v1/products" | python3 -m json.tool 2>/dev/null || echo "Products endpoint not yet ready"
    
    echo ""
    echo "🎯 Setup commands for your service:"
    echo "=================================="
    echo "Health check: curl $RENDER_URL/setup/health"
    echo "Init database: curl -X POST $RENDER_URL/setup/init-db"
    echo "Test products: curl $RENDER_URL/api/v1/products"
    echo "Admin panel: $RENDER_URL/admin"
    echo ""
    echo "Full test: python3 test_deployment.py $RENDER_URL"
else
    echo "Please run this script again with your Render URL"
fi
