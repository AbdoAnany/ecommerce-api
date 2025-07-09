from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()

# JWT blacklist set (in production, use Redis)
blacklisted_tokens = set()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    
    # JWT token blacklist checker
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in blacklisted_tokens
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    
    from app.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    
    from app.categories import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    
    from app.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/api/v1/cart')
    
    from app.orders import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api/v1/orders')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    
    from app.shipping import bp as shipping_bp
    app.register_blueprint(shipping_bp, url_prefix='/api/v1/shipping')
    
    # Health check endpoint
    @app.route('/ping')
    def ping():
        return {'status': 'ok', 'message': 'E-commerce API is running'}
    
    # API info endpoint
    @app.route('/api/v1')
    def api_info():
        return {
            'name': 'E-commerce API',
            'version': 'v1.0.0',
            'description': 'RESTful API for e-commerce platform',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'products': '/api/v1/products',
                'categories': '/api/v1/categories',
                'cart': '/api/v1/cart',
                'orders': '/api/v1/orders',
                'admin': '/api/v1/admin',
                'shipping': '/api/v1/shipping'
            }
        }
    
    return app
