#!/usr/bin/env python3
"""
Script to update a user to admin role
"""

import os
import sys
from app import create_app
from app.models import User, UserRole
from app import db

def update_user_to_admin(user_id):
    """Update a user to admin role by user ID"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Find the user
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User with ID {user_id} not found")
                return False
            
            print(f"📋 Current user details:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Name: {user.get_full_name()}")
            print(f"   Current Role: {user.role.value}")
            print(f"   Active: {user.is_active}")
            print()
            
            # Update to admin
            user.role = UserRole.ADMIN
            user.is_active = True  # Ensure admin is active
            user.is_verified = True  # Ensure admin is verified
            
            db.session.commit()
            
            print(f"✅ User {user.username} (ID: {user.id}) updated to admin successfully!")
            print(f"📧 Email: {user.email}")
            print(f"👤 Role: {user.role.value}")
            print(f"✔️  Active: {user.is_active}")
            print(f"✔️  Verified: {user.is_verified}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating user to admin: {e}")
            return False

def update_user_to_admin_by_email(email):
    """Update a user to admin role by email"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Find the user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ User with email {email} not found")
                return False
            
            print(f"📋 Found user:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Current Role: {user.role.value}")
            print()
            
            # Update to admin
            user.role = UserRole.ADMIN
            user.is_active = True
            user.is_verified = True
            
            db.session.commit()
            
            print(f"✅ User {user.email} updated to admin successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating user to admin: {e}")
            return False

def list_all_users():
    """List all users in the database"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            users = User.query.all()
            
            if not users:
                print("❌ No users found in database")
                return
            
            print(f"👥 Found {len(users)} user(s):")
            print("=" * 60)
            
            for user in users:
                print(f"ID: {user.id} | Email: {user.email} | Username: {user.username}")
                print(f"Name: {user.get_full_name()} | Role: {user.role.value}")
                print(f"Active: {'✅' if user.is_active else '❌'} | Verified: {'✅' if user.is_verified else '❌'}")
                print("-" * 60)
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_user_to_admin.py list                    # List all users")
        print("  python update_user_to_admin.py update_id <user_id>     # Update user by ID")
        print("  python update_user_to_admin.py update_email <email>    # Update user by email")
        print()
        print("Examples:")
        print("  python update_user_to_admin.py list")
        print("  python update_user_to_admin.py update_id 1")
        print("  python update_user_to_admin.py update_email user@example.com")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_all_users()
    
    elif command == "update_id" and len(sys.argv) > 2:
        user_id = int(sys.argv[2])
        update_user_to_admin(user_id)
    
    elif command == "update_email" and len(sys.argv) > 2:
        email = sys.argv[2]
        update_user_to_admin_by_email(email)
    
    else:
        print("❌ Invalid command or missing parameters")
        print("Use 'python update_user_to_admin.py' for usage help")
