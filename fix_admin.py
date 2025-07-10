#!/usr/bin/env python3
"""
Fix existing admin user and complete database setup
"""

import os
import sys
from app import create_app
from app.models import db, User, Product, Category, UserRole
from werkzeug.security import generate_password_hash

def fix_admin_and_setup():
    """Fix admin user and complete setup"""
    print("🔧 Fixing admin user and completing setup...")
    
    # Create Flask app
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        try:
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print(f"👤 Found existing admin user: {admin_user.email}")
                
                # Update admin user password
                admin_user.password_hash = generate_password_hash('admin123')
                admin_user.email = 'admin@example.com'
                admin_user.role = UserRole.ADMIN
                admin_user.is_active = True
                admin_user.is_verified = True
                db.session.commit()
                print("✅ Admin user password reset to: admin123")
            else:
                print("❌ No admin user found")
                return
            
            # Check and create categories if needed
            categories_count = Category.query.count()
            if categories_count == 0:
                print("📁 Creating categories...")
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
                print(f"✅ Created {len(categories)} categories")
            else:
                print(f"ℹ️  Found {categories_count} existing categories")
            
            # Check and create products if needed
            products_count = Product.query.count()
            if products_count == 0:
                print("📦 Creating sample products...")
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
                print(f"✅ Created {len(products)} sample products")
            else:
                print(f"ℹ️  Found {products_count} existing products")
            
            print("\n🎉 Setup completed successfully!")
            print("👤 Admin credentials: admin@example.com / admin123")
            print("🌐 Admin panel: /admin")
            print("📊 API endpoints ready")
            
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_admin_and_setup()
