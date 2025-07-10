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
        
        # Create customer user for testing
        customer_user = User.query.filter_by(email='customer@example.com').first()
        if not customer_user:
            customer_user = User(
                username='customer',
                email='customer@example.com',
                password_hash=generate_password_hash('customer123'),
                first_name='Customer',
                last_name='User',
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=True
            )
            db.session.add(customer_user)
            print("Created customer user")
        else:
            # Update password
            customer_user.password_hash = generate_password_hash('customer123')
            print("Updated customer user password")
        
        # Commit users first
        db.session.commit()
        
        # Create sample categories (if they don't exist)
        categories_count = Category.query.count()
        if categories_count == 0:
            categories = [
                Category(name_en='Electronics', description_en='Electronic devices and gadgets', slug='electronics'),
                Category(name_en='Clothing', description_en='Fashion and apparel', slug='clothing'),
                Category(name_en='Books', description_en='Books and literature', slug='books'),
                Category(name_en='Home & Garden', description_en='Home improvement and gardening', slug='home-garden'),
                Category(name_en='Sports', description_en='Sports and outdoor equipment', slug='sports')
            ]
            
            for category in categories:
                db.session.add(category)
            
            # Commit categories before products
            db.session.commit()
            categories_created = len(categories)
        else:
            categories_created = 0
        
        # Create sample products (if they don't exist)
        products_count = Product.query.count()
        if products_count == 0:
            # Get actual category IDs from database
            electronics_cat = Category.query.filter_by(slug='electronics').first()
            clothing_cat = Category.query.filter_by(slug='clothing').first()
            
            if electronics_cat and clothing_cat:
                print(f"Found categories: Electronics ID={electronics_cat.id}, Clothing ID={clothing_cat.id}")
                
                products_data = [
                    {
                        'name_en': 'Dove Shower Gel 500ml',
                        'name_ar': 'دوف شاور جل 500 مل',
                        'description_en': 'Dove Moisturizing Shower Gel, 500ml – enriched with skin-natural nutrients to leave your skin soft, smooth, and hydrated after every shower.',
                        'description_ar': 'دوف جل استحمام مرطب 500 مل – غني بالمغذيات الطبيعية التي تترك بشرتك ناعمة ورطبة بعد كل استخدام.',
                        'thumbnail': 'https://cdn.example.com/03/prod/44871-P.jfif',
                        'sku': '6221030009120',
                        'slug': 'dove-shower-gel-500ml',
                        'price': 57.00,
                        'discount_price': 0,
                        'currency': 'EGP',
                        'stock_quantity': 10,
                        'min_stock': 0,
                        'availability': 'in_stock',
                        'brand': 'Dove',
                        'unit_measure_en': 'milliliter',
                        'unit_measure_ar': 'ملليلتر',
                        'unit_value': 500,
                        'package_type': 'Bottle',
                        'country_of_origin': 'Germany',
                        'ingredients': '["Water", "Glycerin", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine", "Fragrance", "Citric Acid", "Sodium Benzoate"]',
                        'usage_instructions_en': 'Apply a small amount to wet skin, lather, and rinse thoroughly.',
                        'usage_instructions_ar': 'ضعي كمية صغيرة على البشرة المبللة، دلكي بلطف، ثم اشطفي جيدًا.',
                        'warnings_en': 'For external use only. Avoid contact with eyes.',
                        'warnings_ar': 'للاستخدام الخارجي فقط. تجنب ملامسة العينين.',
                        'min_qty': 1,
                        'step_qty': 1,
                        'max_qty': 10,
                        'is_featured': False,
                        'is_new': False,
                        'is_on_sale': False,
                        'is_organic': False,
                        'category_id': electronics_cat.id,
                        'is_active': True
                    },
                    {
                        'name_en': 'iPhone 15',
                        'name_ar': 'آيفون 15',
                        'description_en': 'Latest Apple smartphone with advanced features',
                        'description_ar': 'أحدث هاتف ذكي من آبل مع ميزات متقدمة',
                        'sku': 'IPHONE15-001',
                        'slug': 'iphone-15',
                        'price': 999.99,
                        'discount_price': 0,
                        'currency': 'USD',
                        'stock_quantity': 50,
                        'min_stock': 5,
                        'availability': 'in_stock',
                        'brand': 'Apple',
                        'unit_measure_en': 'piece',
                        'unit_measure_ar': 'قطعة',
                        'unit_value': 1,
                        'package_type': 'Box',
                        'country_of_origin': 'China',
                        'min_qty': 1,
                        'step_qty': 1,
                        'max_qty': 5,
                        'is_featured': True,
                        'is_new': True,
                        'is_on_sale': False,
                        'is_organic': False,
                        'category_id': electronics_cat.id,
                        'is_active': True
                    },
                    {
                        'name_en': 'Nike Air Jordan',
                        'name_ar': 'نايك اير جوردان',
                        'description_en': 'Premium basketball shoes',
                        'description_ar': 'حذاء كرة السلة المميز',
                        'sku': 'NIKE-JORDAN-001',
                        'slug': 'nike-air-jordan',
                        'price': 149.99,
                        'discount_price': 20.00,
                        'currency': 'USD',
                        'stock_quantity': 100,
                        'min_stock': 10,
                        'availability': 'in_stock',
                        'brand': 'Nike',
                        'unit_measure_en': 'pair',
                        'unit_measure_ar': 'زوج',
                        'unit_value': 1,
                        'package_type': 'Box',
                        'country_of_origin': 'Vietnam',
                        'min_qty': 1,
                        'step_qty': 1,
                        'max_qty': 10,
                        'is_featured': False,
                        'is_new': False,
                        'is_on_sale': True,
                        'is_organic': False,
                        'category_id': clothing_cat.id,
                        'is_active': True
                    }
                ]
                
                products_created = 0
                for product_data in products_data:
                    try:
                        print(f"Creating product: {product_data['name_en']} with slug: {product_data['slug']}")
                        product = Product(**product_data)
                        print(f"Product created with slug: {product.slug}")
                        db.session.add(product)
                        db.session.commit()
                        products_created += 1
                        print(f"Product {product.name_en} committed successfully")
                    except Exception as e:
                        print(f"Failed to create product {product_data['name_en']}: {str(e)}")
                        db.session.rollback()
                        continue
            else:
                products_created = 0
                print("Categories not found, skipping product creation")
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
