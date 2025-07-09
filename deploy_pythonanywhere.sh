#!/bin/bash

# 🐍 PythonAnywhere Deployment Setup Script

echo "🐍 PythonAnywhere Deployment Setup"
echo "=================================="

# Generate secure keys
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

echo ""
echo "🔑 Generated secure keys (save these!):"
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"

# Create PythonAnywhere specific files
echo ""
echo "📄 Creating PythonAnywhere configuration files..."

# Create WSGI file for PythonAnywhere
cat > pythonanywhere_wsgi.py << 'EOF'
#!/usr/bin/python3.10

import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, '/home/yourusername/ecommerce_api')

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'
# Set your actual values here:
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'
os.environ['DATABASE_URL'] = 'mysql+pymysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$ecommerce'

from app import create_app
application = create_app()

if __name__ == "__main__":
    application.run()
EOF

# Create MySQL configuration
cat > mysql_setup.sql << 'EOF'
-- PythonAnywhere MySQL Database Setup
-- Run these commands in the MySQL console

CREATE DATABASE yourusername$ecommerce CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE yourusername$ecommerce;

-- The database is now ready for your Flask app
-- Flask-Migrate will create the tables
EOF

# Create environment file template
cat > .env.pythonanywhere << 'EOF'
# PythonAnywhere Environment Variables
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=mysql+pymysql://yourusername:yourpassword@yourusername.mysql.pythonanywhere-services.com/yourusername$ecommerce
EOF

echo "✅ Created pythonanywhere_wsgi.py"
echo "✅ Created mysql_setup.sql"
echo "✅ Created .env.pythonanywhere template"

echo ""
echo "🚀 PythonAnywhere Deployment Steps:"
echo "===================================="
echo ""
echo "1. Sign up at https://www.pythonanywhere.com (free account)"
echo ""
echo "2. Open a Bash console and upload your code:"
echo "   $ git clone https://github.com/yourusername/ecommerce_api.git"
echo "   $ cd ecommerce_api"
echo ""
echo "3. Create virtual environment:"
echo "   $ python3.10 -m venv venv"
echo "   $ source venv/bin/activate"
echo "   $ pip install -r requirements.txt"
echo ""
echo "4. Setup MySQL Database:"
echo "   - Go to Databases tab in dashboard"
echo "   - Create new database: yourusername\$ecommerce"
echo "   - Note the connection details"
echo "   - Update pythonanywhere_wsgi.py with your details"
echo ""
echo "5. Configure Web App:"
echo "   - Go to Web tab"
echo "   - Create new web app"
echo "   - Choose Manual configuration → Python 3.10"
echo "   - Set source code: /home/yourusername/ecommerce_api"
echo "   - Set virtualenv: /home/yourusername/ecommerce_api/venv"
echo "   - Replace WSGI file content with pythonanywhere_wsgi.py"
echo ""
echo "6. Update WSGI Configuration:"
echo "   - Replace 'yourusername' with your actual username"
echo "   - Replace 'yourpassword' with your MySQL password"
echo "   - Update SECRET_KEY: $SECRET_KEY"
echo "   - Update JWT_SECRET_KEY: $JWT_SECRET_KEY"
echo ""
echo "7. Setup Database:"
echo "   $ python deploy.py"
echo "   $ python create_sample_data.py"
echo ""
echo "8. Configure Static Files (optional):"
echo "   - URL: /static/"
echo "   - Directory: /home/yourusername/ecommerce_api/static/"
echo ""
echo "✅ Your API will be available at: https://yourusername.pythonanywhere.com"
echo ""
echo "📊 Test endpoints:"
echo "   - Health: https://yourusername.pythonanywhere.com/ping"
echo "   - API Info: https://yourusername.pythonanywhere.com/api/v1"
echo ""
echo "🔗 Update your Postman collection base_url to your PythonAnywhere URL!"

# Save keys to a file for reference
echo "# PythonAnywhere Environment Variables" > pythonanywhere_env_vars.txt
echo "FLASK_ENV=production" >> pythonanywhere_env_vars.txt
echo "DEBUG=False" >> pythonanywhere_env_vars.txt
echo "SECRET_KEY=$SECRET_KEY" >> pythonanywhere_env_vars.txt
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> pythonanywhere_env_vars.txt
echo "" >> pythonanywhere_env_vars.txt
echo "# Add these to your pythonanywhere_wsgi.py file" >> pythonanywhere_env_vars.txt

echo ""
echo "💾 Keys saved to: pythonanywhere_env_vars.txt"
echo "📄 Configuration files created for easy setup!"
