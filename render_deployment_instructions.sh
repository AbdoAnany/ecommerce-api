#!/bin/bash

# Complete Render Deployment Setup Script
# This script provides step-by-step instructions for deploying to Render

echo "🚀 Flask E-commerce API - Render Deployment Setup"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Make sure app.py and requirements.txt are present"
    exit 1
fi

echo "✅ Project files detected"
echo ""

# Check if changes are committed to git
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Please commit and push all changes before deploying to Render"
    echo ""
    echo "   Run these commands:"
    echo "   git add ."
    echo "   git commit -m 'Ready for Render deployment'"
    echo "   git push origin main"
    echo ""
fi

# Check if repository is on GitHub
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ $REPO_URL == *"github.com"* ]]; then
    echo "✅ GitHub repository detected: $REPO_URL"
else
    echo "❌ Error: This project needs to be on GitHub for Render deployment"
    echo "   Please push your code to GitHub first"
    exit 1
fi

echo ""
echo "📋 STEP-BY-STEP RENDER DEPLOYMENT INSTRUCTIONS"
echo "=============================================="
echo ""

echo "1️⃣  CREATE NEW WEB SERVICE ON RENDER"
echo "   • Go to: https://dashboard.render.com/create?type=web"
echo "   • Connect your GitHub account if not already connected"
echo "   • Select this repository: $(basename $(git remote get-url origin) .git)"
echo ""

echo "2️⃣  CONFIGURE THE SERVICE"
echo "   • Name: ecommerce-api (or your preferred name)"
echo "   • Environment: Python 3"
echo "   • Build Command: pip install -r requirements.txt"
echo "   • Start Command: gunicorn --bind 0.0.0.0:\$PORT wsgi:application"
echo "   • Plan: Free (or your preferred plan)"
echo ""

echo "3️⃣  ADD ENVIRONMENT VARIABLES"
echo "   In the 'Environment' section, add these variables:"
echo ""
cat << 'EOF'
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=t8_yhiC7NCXaRy_cTehEUo5r54RUuq3yoibuzOMN5-4
   JWT_SECRET_KEY=w6lBZRztm7O-WUk6tdAhFbR0fK1TtCRvO-SZBTyG0yY
   DATABASE_URL=(will be added after database setup)
EOF
echo ""

echo "4️⃣  CREATE POSTGRESQL DATABASE"
echo "   • Go to: https://dashboard.render.com/create?type=pgsql"
echo "   • Name: ecommerce-db (or your preferred name)"
echo "   • Plan: Free"
echo "   • After creation, copy the 'Internal Database URL'"
echo ""

echo "5️⃣  ADD DATABASE_URL TO WEB SERVICE"
echo "   • Go back to your web service settings"
echo "   • Add environment variable:"
echo "     DATABASE_URL=<paste the Internal Database URL here>"
echo ""

echo "6️⃣  DEPLOY THE SERVICE"
echo "   • Click 'Create Web Service'"
echo "   • Wait for the deployment to complete (this may take several minutes)"
echo ""

echo "7️⃣  GET YOUR SERVICE URL"
echo "   After successful deployment, your API will be available at:"
echo "   https://[your-service-name].onrender.com"
echo ""
echo "   The exact URL will be shown in the Render dashboard"
echo ""

echo "📝 IMPORTANT NOTES:"
echo "==================="
echo ""
echo "• Free tier services may experience cold starts (first request may be slow)"
echo "• Services may sleep after 15 minutes of inactivity"
echo "• Database connections are limited on the free tier"
echo "• Check deployment logs if you encounter issues"
echo ""

echo "🔧 TROUBLESHOOTING:"
echo "==================="
echo ""
echo "If deployment fails:"
echo "• Check the build logs in Render dashboard"
echo "• Verify all environment variables are set correctly"
echo "• Ensure the DATABASE_URL is the Internal Database URL"
echo "• Check that all dependencies in requirements.txt are compatible"
echo ""

echo "✅ POST-DEPLOYMENT VERIFICATION:"
echo "================================="
echo ""
echo "After deployment completes:"
echo "1. Note the actual service URL from Render dashboard"
echo "2. Test the health endpoint: [your-url]/health"
echo "3. Test the API endpoints using the provided examples"
echo "4. Update this deployment check script with the correct URL"
echo ""

echo "📊 Files included in this deployment:"
echo "====================================="
ls -la | grep -E "(app\.py|wsgi\.py|requirements\.txt|config\.py|render\.yaml|runtime\.txt|\.python-version)"
echo ""

echo "🎯 Ready to deploy! Follow the steps above in the Render dashboard."
echo ""
