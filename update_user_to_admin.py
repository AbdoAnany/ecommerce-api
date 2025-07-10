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

def reset_user_password(user_id, new_password):
    """Reset a user's password by user ID"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Find the user
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User with ID {user_id} not found")
                return False
            
            print(f"📋 Resetting password for user:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Name: {user.get_full_name()}")
            print()
            
            # Set new password
            user.set_password(new_password)
            user.reset_token = None  # Clear any existing reset token
            
            db.session.commit()
            
            print(f"✅ Password reset successfully for {user.username}!")
            print(f"🔑 New password: {new_password}")
            print(f"📧 Email: {user.email}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting password: {e}")
            return False

def reset_user_password_by_email(email, new_password):
    """Reset a user's password by email"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Find the user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ User with email {email} not found")
                return False
            
            print(f"📋 Resetting password for:")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role.value}")
            print()
            
            # Set new password
            user.set_password(new_password)
            user.reset_token = None  # Clear any existing reset token
            
            db.session.commit()
            
            print(f"✅ Password reset successfully for {user.email}!")
            print(f"🔑 New password: {new_password}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting password: {e}")
            return False

def reset_admin_password():
    """Reset the main admin password to default"""
    
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Find admin user
            admin = User.query.filter_by(email='admin@example.com').first()
            
            if not admin:
                print("❌ Admin user not found")
                return False
            
            print(f"📋 Resetting admin password:")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print()
            
            # Reset to default password
            admin.set_password('admin123')
            admin.reset_token = None
            
            db.session.commit()
            
            print("✅ Admin password reset to default!")
            print("🔑 Email: admin@example.com")
            print("🔑 Password: admin123")
            print("⚠️  Please change this password after login!")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting admin password: {e}")
            return False

def generate_secure_password():
    """Generate a secure random password"""
    import secrets
    import string
    
    # Generate a 12-character password with uppercase, lowercase, digits, and symbols
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("👥 User Management Script")
        print("=" * 50)
        print("Usage:")
        print("  python update_user_to_admin.py list                              # List all users")
        print("  python update_user_to_admin.py update_id <user_id>               # Update user by ID to admin")
        print("  python update_user_to_admin.py update_email <email>              # Update user by email to admin")
        print("  python update_user_to_admin.py reset_password_id <user_id> <pwd> # Reset password by user ID")
        print("  python update_user_to_admin.py reset_password_email <email> <pwd># Reset password by email")
        print("  python update_user_to_admin.py reset_admin                       # Reset admin password to default")
        print("  python update_user_to_admin.py generate_password                 # Generate secure password")
        print()
        print("Examples:")
        print("  python update_user_to_admin.py list")
        print("  python update_user_to_admin.py update_id 1")
        print("  python update_user_to_admin.py update_email user@example.com")
        print("  python update_user_to_admin.py reset_password_id 1 newpassword123")
        print("  python update_user_to_admin.py reset_password_email user@example.com newpass123")
        print("  python update_user_to_admin.py reset_admin")
        print("  python update_user_to_admin.py generate_password")
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
    
    elif command == "reset_password_id" and len(sys.argv) > 3:
        user_id = int(sys.argv[2])
        new_password = sys.argv[3]
        reset_user_password(user_id, new_password)
    
    elif command == "reset_password_email" and len(sys.argv) > 3:
        email = sys.argv[2]
        new_password = sys.argv[3]
        reset_user_password_by_email(email, new_password)
    
    elif command == "reset_admin":
        reset_admin_password()
    
    elif command == "generate_password":
        password = generate_secure_password()
        print(f"🔑 Generated secure password: {password}")
        print("💡 Copy this password and use it with the reset commands")
    
    else:
        print("❌ Invalid command or missing parameters")
        print("Use 'python update_user_to_admin.py' for usage help")
