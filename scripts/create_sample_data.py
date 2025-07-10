#!/usr/bin/env python3

import os
import sys
from app import create_app, db
from app.models import User, Category, Product, Tag, UserRole
from datetime import datetime, timezone
from decimal import Decimal

def create_sample_data():
    """Create sample data for testing"""
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        print("Creating sample data...")
        
        # Create admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user: admin@example.com / admin123")
        
        # Create customer user
        customer = User.query.filter_by(email='customer@example.com').first()
        if not customer:
            customer = User(
                email='customer@example.com',
                username='customer',
                first_name='John',
                last_name='Doe',
                role=UserRole.CUSTOMER,
                is_active=True,
                is_verified=True
            )
            customer.set_password('customer123')
            db.session.add(customer)
            print("Created customer user: customer@example.com / customer123")
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'description': 'Home improvement and gardening'},
            {'name': 'Sports', 'description': 'Sports and outdoor equipment'}
        ]
        
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    slug=cat_data['name'].lower().replace(' ', '-').replace('&', 'and'),
                    is_active=True
                )
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
        
        # Commit categories first
        db.session.commit()
        
        # Create tags
        tag_names = ['new', 'sale', 'featured', 'bestseller', 'limited', 'eco-friendly']
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                print(f"Created tag: {tag_name}")
        
        # Commit tags
        db.session.commit()
        
        # Create sample products
        electronics = Category.query.filter_by(name='Electronics').first()
        clothing = Category.query.filter_by(name='Clothing').first()
        books = Category.query.filter_by(name='Books').first()
        
        new_tag = Tag.query.filter_by(name='new').first()
        sale_tag = Tag.query.filter_by(name='sale').first()
        featured_tag = Tag.query.filter_by(name='featured').first()
        
        products_data = [
            {
                'name': 'Smartphone Pro X',
                'description': 'Latest smartphone with advanced features and high-quality camera.',
                'short_description': 'Premium smartphone with 128GB storage',
                'sku': 'PHONE-001',
                'price': Decimal('899.99'),
                'compare_price': Decimal('999.99'),
                'stock_quantity': 50,
                'category': electronics,
                'tags': [new_tag, featured_tag],
                'is_featured': True
            },
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'High-quality wireless headphones with noise cancellation.',
                'short_description': 'Premium wireless headphones',
                'sku': 'HEAD-001',
                'price': Decimal('199.99'),
                'stock_quantity': 30,
                'category': electronics,
                'tags': [sale_tag],
                'is_featured': False
            },
            {
                'name': 'Cotton T-Shirt',
                'description': 'Comfortable 100% cotton t-shirt in various colors.',
                'short_description': 'Comfortable cotton t-shirt',
                'sku': 'SHIRT-001',
                'price': Decimal('24.99'),
                'stock_quantity': 100,
                'category': clothing,
                'tags': [new_tag],
                'is_featured': False
            },
            {
                'name': 'Programming Book: Python Mastery',
                'description': 'Complete guide to Python programming for beginners and experts.',
                'short_description': 'Complete Python programming guide',
                'sku': 'BOOK-001',
                'price': Decimal('49.99'),
                'stock_quantity': 25,
                'category': books,
                'tags': [featured_tag],
                'is_featured': True
            }
        ]
        
        for prod_data in products_data:
            product = Product.query.filter_by(sku=prod_data['sku']).first()
            if not product:
                tags = prod_data.pop('tags', [])
                product = Product(**prod_data)
                product.slug = prod_data['name'].lower().replace(' ', '-').replace(':', '')
                
                # Add tags
                for tag in tags:
                    product.tags.append(tag)
                
                db.session.add(product)
                print(f"Created product: {prod_data['name']}")
        
        # Commit all changes
        db.session.commit()
        print("Sample data created successfully!")
        
        # Print summary
        print(f"\nSummary:")
        print(f"Users: {User.query.count()}")
        print(f"Categories: {Category.query.count()}")
        print(f"Products: {Product.query.count()}")
        print(f"Tags: {Tag.query.count()}")

if __name__ == '__main__':
    create_sample_data()
