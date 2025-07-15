#!/usr/bin/env python3
"""
Database initialization script for production deployments
"""

import os
import sys
from app import create_app
from app.models import db, User, Product, Category, Order, OrderItem, CartItem, UserRole
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and sample data"""
    print("🔄 Initializing database...")
    
    # Create Flask app
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if admin user already exists
            admin_user = User.query.filter_by(email='admin@example.com').first()
            if not admin_user:
                print("👤 Creating admin user...")
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
                
                # Create sample categories
                print("📁 Creating sample categories...")
                categories = [
                    Category(
                        name={'en': 'Electronics', 'ar': 'إلكترونيات'},
                        description={'en': 'Electronic devices and gadgets', 'ar': 'الأجهزة والمعدات الإلكترونية'},
                        slug='electronics'
                    ),
                    Category(
                        name={'en': 'Clothing', 'ar': 'ملابس'},
                        description={'en': 'Fashion and apparel', 'ar': 'الأزياء والملابس'},
                        slug='clothing'
                    ),
                    Category(
                        name={'en': 'Books', 'ar': 'كتب'},
                        description={'en': 'Books and literature', 'ar': 'الكتب والأدب'},
                        slug='books'
                    ),
                    Category(
                        name={'en': 'Home & Garden', 'ar': 'المنزل والحديقة'},
                        description={'en': 'Home improvement and gardening', 'ar': 'تحسين المنزل والبستنة'},
                        slug='home-garden'
                    ),
                    Category(
                        name={'en': 'Sports', 'ar': 'رياضة'},
                        description={'en': 'Sports and outdoor equipment', 'ar': 'معدات رياضية وخارجية'},
                        slug='sports'
                    )
                ]
                
                for category in categories:
                    db.session.add(category)
                
                db.session.commit()
                print("✅ Sample categories created")
                
                # Create sample products
                print("📦 Creating sample products...")
                products = [
                    Product(
                        name={'en': 'iPhone 15', 'ar': 'آيفون 15'},
                        description={'en': 'Latest Apple smartphone with advanced features', 'ar': 'أحدث هاتف ذكي من آبل مع ميزات متقدمة'},
                        sku='IPHONE15-001',
                        price=999.99,
                        quantity=50,
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
                    ),
                    Product(
                        name='Python Programming Book',
                        description='Learn Python programming from scratch',
                        sku='PYTHON-BOOK-001',
                        price=39.99,
                        stock_quantity=200,
                        category_id=3,
                        is_active=True
                    ),
                    Product(
                        name='Garden Tool Set',
                        description='Complete set of gardening tools',
                        sku='GARDEN-TOOLS-001',
                        price=79.99,
                        stock_quantity=75,
                        category_id=4,
                        is_active=True
                    )
                ]
                
                for product in products:
                    db.session.add(product)
                
                db.session.commit()
                print("✅ Sample products created")
                
                print("🎉 Database initialization completed successfully!")
                print(f"📊 Created {len(categories)} categories and {len(products)} products")
                print("👤 Admin user: admin@example.com / admin123")
                
            else:
                print("ℹ️  Admin user already exists, skipping sample data creation")
                print("✅ Database tables verified")
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()
            raise
            
if __name__ == "__main__":
    init_database()
