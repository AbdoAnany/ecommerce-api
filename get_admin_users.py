#!/usr/bin/env python3
"""
Script to check and retrieve admin users from the database
"""

import os
import sys
from app import create_app
from app.models import User, UserRole

def check_admin_users():
    """Check and display admin users in the database"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        print("🔍 Checking Admin Users")
        print("=" * 50)
        
        # Get all admin users
        admin_users = User.query.filter_by(role=UserRole.ADMIN).all()
        
        if not admin_users:
            print("❌ No admin users found in the database")
            print("\n💡 To create an admin user:")
            print("   1. Run database initialization: /setup/init-db")
            print("   2. Or create manually using User.role = UserRole.ADMIN")
            return
        
        print(f"✅ Found {len(admin_users)} admin user(s):")
        print()
        
        for i, admin in enumerate(admin_users, 1):
            print(f"👤 Admin User #{i}:")
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Name: {admin.get_full_name()}")
            print(f"   Active: {'✅' if admin.is_active else '❌'}")
            print(f"   Verified: {'✅' if admin.is_verified else '❌'}")
            print(f"   Created: {admin.created_at}")
            print(f"   Last Login: {admin.last_login or 'Never'}")
            print()
        
        # Additional statistics
        active_admins = [a for a in admin_users if a.is_active]
        verified_admins = [a for a in admin_users if a.is_verified]
        
        print("📊 Admin Statistics:")
        print(f"   Total Admins: {len(admin_users)}")
        print(f"   Active Admins: {len(active_admins)}")
        print(f"   Verified Admins: {len(verified_admins)}")
        
        if admin_users:
            print("\n🔐 Login Information:")
            main_admin = admin_users[0]  # First admin user
            print(f"   Email: {main_admin.email}")
            print("   Password: admin123 (default)")
            print("   ⚠️  Change password after first login!")

def get_admin_by_email(email):
    """Get specific admin user by email"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        admin = User.query.filter_by(email=email, role=UserRole.ADMIN).first()
        
        if admin:
            print(f"✅ Admin user found:")
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Name: {admin.get_full_name()}")
            print(f"   Active: {admin.is_active}")
            print(f"   Verified: {admin.is_verified}")
            return admin
        else:
            print(f"❌ No admin user found with email: {email}")
            return None

def create_admin_user(email, username, first_name, last_name, password):
    """Create a new admin user"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"❌ User already exists with email '{email}' or username '{username}'")
            return None
        
        # Create new admin user
        admin = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        admin.set_password(password)
        
        try:
            from app import db
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Admin user created successfully:")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Password: {password}")
            print(f"   ID: {admin.id}")
            
            return admin
            
        except Exception as e:
            from app import db
            db.session.rollback()
            print(f"❌ Failed to create admin user: {e}")
            return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            check_admin_users()
        
        elif command == "get" and len(sys.argv) > 2:
            email = sys.argv[2]
            get_admin_by_email(email)
        
        elif command == "create" and len(sys.argv) > 6:
            email = sys.argv[2]
            username = sys.argv[3]
            first_name = sys.argv[4]
            last_name = sys.argv[5]
            password = sys.argv[6]
            create_admin_user(email, username, first_name, last_name, password)
        
        else:
            print("Usage:")
            print("  python get_admin_users.py check")
            print("  python get_admin_users.py get <email>")
            print("  python get_admin_users.py create <email> <username> <first_name> <last_name> <password>")
    
    else:
        # Default: check admin users
        check_admin_users()
