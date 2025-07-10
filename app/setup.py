#!/usr/bin/env python3
"""
Simple database setup endpoint for manual initialization
"""

from flask import Blueprint, jsonify
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
                    price=999.99,
                    stock_quantity=50,
                    category_id=1,
                    is_active=True
                ),
                Product(
                    name='MacBook Pro',
                    description='Powerful laptop for professionals',
                    price=1999.99,
                    stock_quantity=25,
                    category_id=1,
                    is_active=True
                ),
                Product(
                    name='Nike Air Jordan',
                    description='Premium basketball shoes',
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
