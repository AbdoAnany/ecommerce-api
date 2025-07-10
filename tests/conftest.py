import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Product, Category, UserRole

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, app_instance = tempfile.mkstemp()
    
    app_instance = create_app('testing')
    app_instance.config['TESTING'] = True
    app_instance.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app_instance.config['WTF_CSRF_ENABLED'] = False
    app_instance.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(app_instance)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def customer_user(app):
    """Create a customer user for testing."""
    with app.app_context():
        user = User(
            username='customer',
            email='customer@test.com',
            first_name='Customer',
            last_name='User',
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        user.set_password('customer123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def sample_category(app):
    """Create a sample category for testing."""
    with app.app_context():
        category = Category(
            name='Electronics',
            description='Electronic devices',
            slug='electronics'
        )
        db.session.add(category)
        db.session.commit()
        return category

@pytest.fixture
def sample_product(app, sample_category):
    """Create a sample product for testing."""
    with app.app_context():
        product = Product(
            name='Test Product',
            description='A test product',
            sku='TEST-001',
            slug='test-product',
            price=99.99,
            stock_quantity=10,
            category_id=sample_category.id,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()
        return product

@pytest.fixture
def admin_headers(client, admin_user):
    """Get authorization headers for admin user."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    assert response.status_code == 200
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def customer_headers(client, customer_user):
    """Get authorization headers for customer user."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'customer@test.com',
        'password': 'customer123'
    })
    assert response.status_code == 200
    data = response.get_json()
    token = data['data']['access_token']
    return {'Authorization': f'Bearer {token}'}
