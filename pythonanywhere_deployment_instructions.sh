#!/bin/bash

# Complete PythonAnywhere Deployment Setup Script
# This script provides step-by-step instructions for deploying to PythonAnywhere

echo "🐍 Flask E-commerce API - PythonAnywhere Deployment Setup"
echo "========================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Make sure app.py and requirements.txt are present"
    exit 1
fi

echo "✅ Project files detected"
echo ""

echo "📋 STEP-BY-STEP PYTHONANYWHERE DEPLOYMENT INSTRUCTIONS"
echo "======================================================="
echo ""

echo "1️⃣  CREATE PYTHONANYWHERE ACCOUNT"
echo "   • Go to: https://www.pythonanywhere.com/pricing/"
echo "   • Sign up for a free account (or upgrade for more features)"
echo "   • Free accounts get: yourusername.pythonanywhere.com domain"
echo ""

echo "2️⃣  UPLOAD YOUR CODE"
echo "   Option A: Git Clone (Recommended)"
echo "   • Open a Bash console in PythonAnywhere"
echo "   • Run: git clone https://github.com/AbdoAnany/ecommerce-api.git"
echo "   • Navigate to the project: cd ecommerce-api"
echo ""
echo "   Option B: Upload Files"
echo "   • Use the Files tab to upload your project files"
echo "   • Create a new directory: /home/yourusername/ecommerce-api"
echo ""

echo "3️⃣  CREATE MYSQL DATABASE"
echo "   • Go to the 'Databases' tab in your dashboard"
echo "   • Create a new MySQL database"
echo "   • Note down the database details:"
echo "     - Database name: yourusername\$ecommerce"
echo "     - Host: yourusername.mysql.pythonanywhere-services.com"
echo "     - Username: yourusername"
echo "     - Password: (set your own)"
echo ""

echo "4️⃣  INSTALL DEPENDENCIES"
echo "   • Open a Bash console"
echo "   • Navigate to your project: cd ~/ecommerce-api"
echo "   • Install packages: pip3.10 install --user -r requirements.txt"
echo ""

echo "5️⃣  CONFIGURE ENVIRONMENT"
echo "   • Copy the environment file: cp .env.pythonanywhere .env"
echo "   • Edit the .env file with your database details:"
echo ""
cat << 'EOF'
     DATABASE_URL=mysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$ecommerce
     SECRET_KEY=t8_yhiC7NCXaRy_cTehEUo5r54RUuq3yoibuzOMN5-4
     JWT_SECRET_KEY=w6lBZRztm7O-WUk6tdAhFbR0fK1TtCRvO-SZBTyG0yY
     FLASK_ENV=production
     DEBUG=False
EOF
echo ""

echo "6️⃣  SETUP DATABASE TABLES"
echo "   • In a Bash console, run:"
echo "   cd ~/ecommerce-api"
echo "   python3.10 -c \"from app import app; from app.models import db; app.app_context().push(); db.create_all()\""
echo ""

echo "7️⃣  CONFIGURE WEB APP"
echo "   • Go to the 'Web' tab in your dashboard"
echo "   • Click 'Add a new web app'"
echo "   • Choose 'Manual configuration'"
echo "   • Choose Python 3.10"
echo "   • Set these configurations:"
echo ""
echo "   Source code: /home/yourusername/ecommerce-api"
echo "   Working directory: /home/yourusername/ecommerce-api"
echo "   WSGI configuration file: /var/www/yourusername_pythonanywhere_com_wsgi.py"
echo ""

echo "8️⃣  CONFIGURE WSGI FILE"
echo "   • Click on the WSGI configuration file link"
echo "   • Replace the entire content with the provided pythonanywhere_wsgi.py file"
echo "   • Update the username in the file to match yours"
echo ""

echo "9️⃣  ENABLE YOUR WEB APP"
echo "   • Click the green 'Reload' button"
echo "   • Your API will be available at: https://yourusername.pythonanywhere.com"
echo ""

echo "📝 IMPORTANT NOTES:"
echo "==================="
echo ""
echo "• Free accounts are limited to one web app"
echo "• Free accounts have CPU seconds limitations"
echo "• Database connections may timeout on free tier"
echo "• Use Python 3.10 for best compatibility"
echo ""

echo "🔧 TROUBLESHOOTING:"
echo "==================="
echo ""
echo "If deployment fails:"
echo "• Check the error logs in the Web tab"
echo "• Verify database connection in a console"
echo "• Ensure all packages are installed with --user flag"
echo "• Check that the WSGI file has correct paths"
echo ""

echo "✅ POST-DEPLOYMENT VERIFICATION:"
echo "================================="
echo ""
echo "After deployment completes:"
echo "1. Test the health endpoint: https://yourusername.pythonanywhere.com/health"
echo "2. Check error logs if the site doesn't load"
echo "3. Test database connectivity by creating a user"
echo ""

echo "📊 Files prepared for PythonAnywhere:"
echo "====================================="
ls -la | grep -E "(pythonanywhere|mysql|\.env)"
echo ""

echo "🎯 Ready to deploy! Follow the steps above in PythonAnywhere dashboard."
echo ""

# Show the WSGI file content
echo "📄 WSGI Configuration (copy this to your WSGI file):"
echo "==================================================="
cat pythonanywhere_wsgi.py
echo ""
