import unittest
import json
import os
import tempfile
from app import create_app, db
from app.models import User, Product, Category, UserRole, Order, CartItem

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.client = self.app.test_client()
        
        # Create all tables
        db.create_all()
        
        # Create test users
        self.create_test_users()
        
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_users(self):
        """Create test users for authentication tests."""
        # Create admin user
        self.admin_user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        self.admin_user.set_password('admin123')
        db.session.add(self.admin_user)
        
        # Create customer user
        self.customer_user = User(
            username='customer',
            email='customer@test.com',
            first_name='Customer',
            last_name='User',
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        self.customer_user.set_password('customer123')
        db.session.add(self.customer_user)
        
        db.session.commit()
    
    def get_admin_token(self):
        """Get authentication token for admin user."""
        response = self.client.post('/api/v1/auth/login', 
                                  data=json.dumps({
                                      'email': 'admin@test.com',
                                      'password': 'admin123'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        return data['data']['access_token']
    
    def get_customer_token(self):
        """Get authentication token for customer user."""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'email': 'customer@test.com',
                                      'password': 'customer123'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        return data['data']['access_token']
    
    def get_admin_headers(self):
        """Get authorization headers for admin user."""
        token = self.get_admin_token()
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    def get_customer_headers(self):
        """Get authorization headers for customer user."""
        token = self.get_customer_token()
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    def create_sample_category(self, name='Electronics', slug='electronics'):
        """Create a sample category for testing."""
        # Check if category already exists
        existing_category = Category.query.filter_by(slug=slug).first()
        if existing_category:
            return existing_category
            
        category = Category(
            name_en=name,
            description_en='Electronic devices',
            slug=slug,
            slug_en=slug
        )
        db.session.add(category)
        db.session.commit()
        return category
    
    def create_sample_product(self, category_id=None):
        """Create a sample product for testing."""
        if category_id is None:
            category = self.create_sample_category()
            category_id = category.id
        
        product = Product(
            name_en='Test Product',
            description_en='A test product description',
            sku='TEST-001',
            slug='test-product',
            price=99.99,
            stock_quantity=10,
            category_id=category_id,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()
        return product
