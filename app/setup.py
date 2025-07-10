#!/usr/bin/env python3
"""
Simple database setup endpoint for manual initialization
"""

from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Product, Category, Order, OrderItem, CartItem, UserRole
from werkzeug.security import generate_password_hash
import os

setup_bp = Blueprint('setup', __name__, url_prefix='/setup')

@setup_bp.route('/init-db', methods=['POST'])
def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Only allow this in production if explicitly enabled
        if os.getenv('ALLOW_DB_INIT') != 'true':
            return jsonify({'error': 'Database initialization not allowed'}), 403
        
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            # Update existing admin user
            admin_user.password_hash = generate_password_hash('admin123')
            admin_user.email = 'admin@example.com'
            admin_user.role = UserRole.ADMIN
            admin_user.is_active = True
            admin_user.is_verified = True
            print("Updated existing admin user")
        else:
            # Create new admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.session.add(admin_user)
            print("Created new admin user")
        
        # Create sample categories (if they don't exist)
        categories_count = Category.query.count()
        if categories_count == 0:
            categories = [
                Category(name='Electronics', description='Electronic devices and gadgets', slug='electronics'),
                Category(name='Clothing', description='Fashion and apparel', slug='clothing'),
                Category(name='Books', description='Books and literature', slug='books'),
                Category(name='Home & Garden', description='Home improvement and gardening', slug='home-garden'),
                Category(name='Sports', description='Sports and outdoor equipment', slug='sports')
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            categories_created = len(categories)
        else:
            categories_created = 0
        
        # Create sample products (if they don't exist)
        products_count = Product.query.count()
        if products_count == 0:
            products = [
                Product(
                    name='iPhone 15',
                    description='Latest Apple smartphone with advanced features',
                    sku='IPHONE15-001',
                    price=999.99,
                    stock_quantity=50,
                    category_id=1,
                    is_active=True
                ),
                Product(
                    name='MacBook Pro',
                    description='Powerful laptop for professionals',
                    sku='MACBOOK-PRO-001',
                    price=1999.99,
                    stock_quantity=25,
                    category_id=1,
                    is_active=True
                ),
                Product(
                    name='Nike Air Jordan',
                    description='Premium basketball shoes',
                    sku='NIKE-JORDAN-001',
                    price=149.99,
                    stock_quantity=100,
                    category_id=2,
                    is_active=True
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            products_created = len(products)
        else:
            products_created = 0
        
        return jsonify({
            'message': 'Database initialized successfully!',
            'admin_email': 'admin@example.com',
            'admin_password': 'admin123',
            'categories_created': categories_created,
            'products_created': products_created,
            'existing_categories': categories_count,
            'existing_products': products_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database initialization failed: {str(e)}'}), 500

@setup_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        # Try to connect to database
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'message': 'API is running and database is accessible'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@setup_bp.route('/promote-user', methods=['POST'])
def promote_user_to_admin():
    """Promote a user to admin role via setup endpoint"""
    try:
        # Only allow this in production if explicitly enabled
        if os.getenv('ALLOW_DB_INIT') != 'true':
            return jsonify({'error': 'User promotion not allowed'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        user_id = data.get('user_id')
        email = data.get('email')
        
        if not user_id and not email:
            return jsonify({'error': 'Either user_id or email is required'}), 400
        
        # Find user
        if user_id:
            user = User.query.get(user_id)
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already admin
        if user.role == UserRole.ADMIN:
            return jsonify({
                'message': 'User is already an admin',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role.value
                }
            }), 200
        
        # Store previous role
        previous_role = user.role.value
        
        # Promote to admin
        user.role = UserRole.ADMIN
        user.is_active = True
        user.is_verified = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'User promoted to admin successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'previous_role': previous_role,
                'new_role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to promote user: {str(e)}'}), 500

@setup_bp.route('/list-users', methods=['GET'])
def list_users():
    """List all users (for setup purposes)"""
    try:
        # Only allow this in production if explicitly enabled
        if os.getenv('ALLOW_DB_INIT') != 'true':
            return jsonify({'error': 'User listing not allowed'}), 403
        
        users = User.query.all()
        
        user_list = [
            {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
        
        # Count by role
        admin_count = len([u for u in users if u.role == UserRole.ADMIN])
        customer_count = len([u for u in users if u.role == UserRole.CUSTOMER])
        vendor_count = len([u for u in users if u.role == UserRole.VENDOR])
        
        return jsonify({
            'message': 'Users retrieved successfully',
            'total_users': len(users),
            'counts': {
                'admins': admin_count,
                'customers': customer_count,
                'vendors': vendor_count
            },
            'users': user_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list users: {str(e)}'}), 500

@setup_bp.route('/reset-admin-password', methods=['POST'])
def emergency_reset_admin_password():
    """Emergency admin password reset (only when ALLOW_DB_INIT=true)"""
    try:
        # Only allow this when database init is enabled
        if os.getenv('ALLOW_DB_INIT') != 'true':
            return jsonify({'error': 'Emergency reset not allowed. Set ALLOW_DB_INIT=true'}), 403
        
        data = request.get_json() or {}
        new_password = data.get('new_password', 'admin123')
        admin_email = data.get('admin_email', 'admin@example.com')
        
        # Find admin user
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            return jsonify({'error': f'Admin user with email {admin_email} not found'}), 404
        
        # Reset password
        admin_user.set_password(new_password)
        admin_user.role = UserRole.ADMIN  # Ensure admin role
        admin_user.is_active = True
        admin_user.is_verified = True
        admin_user.reset_token = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Admin password reset successfully',
            'admin_email': admin_user.email,
            'new_password': new_password,
            'warning': 'Change this password after login'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500
