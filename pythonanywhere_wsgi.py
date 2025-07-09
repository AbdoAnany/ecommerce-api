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
