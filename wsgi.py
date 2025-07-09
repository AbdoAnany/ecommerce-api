#!/usr/bin/env python3

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app

# Create the Flask application
app = create_app(os.getenv('FLASK_ENV', 'production'))

# For compatibility with different deployment platforms
application = app

if __name__ == "__main__":
    app.run()
