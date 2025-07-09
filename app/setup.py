#!/usr/bin/env python3
"""
Simple database setup endpoint for manual initialization
"""

from flask import Blueprint, jsonify
from app import db
from app.models import User, Product, Category, Order, OrderItem, CartItem
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
        if admin_user:
            return jsonify({
                'message': 'Database already initialized',
                'admin_exists': True
            }), 200
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            is_verified=True
        )
        db.session.add(admin_user)
        
        # Create sample categories
        categories = [
            Category(name='Electronics', description='Electronic devices and gadgets'),
            Category(name='Clothing', description='Fashion and apparel'),
            Category(name='Books', description='Books and literature'),
            Category(name='Home & Garden', description='Home improvement and gardening'),
            Category(name='Sports', description='Sports and outdoor equipment')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
        
        # Create sample products
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
        
        return jsonify({
            'message': 'Database initialized successfully!',
            'admin_email': 'admin@example.com',
            'admin_password': 'admin123',
            'categories_created': len(categories),
            'products_created': len(products)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database initialization failed: {str(e)}'}), 500

@setup_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        # Try to connect to database
        db.session.execute('SELECT 1')
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
