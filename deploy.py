import os
from app import create_app, db
from app.models import *
from flask_migrate import upgrade

def deploy():
    """Run deployment tasks."""
    # Create application instance
    app = create_app(os.getenv('FLASK_ENV') or 'production')
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Migrate database to latest revision
        upgrade()

if __name__ == '__main__':
    deploy()
