from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from sqlalchemy import or_, and_
from app.products import bp
from app.products.schemas import (
    ProductCreateSchema, ProductUpdateSchema, 
    ProductListSchema, ProductDetailSchema
)
from app.models import Product, Category, Tag, User, UserRole
from app import db
import re

def require_admin():
    """Decorator to require admin role"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            
            if not user or user.role != UserRole.ADMIN:
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip()
    slug = re.sub(r'[\s_-]+', '-', slug).lower()
    return slug

@bp.route('', methods=['GET'])
def get_products():
    """Get products with filtering, search, and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', current_app.config['DEFAULT_PAGE_SIZE'], type=int), 
                   current_app.config['MAX_PAGE_SIZE'])
    
    # Filters
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock', type=bool)
    featured = request.args.get('featured', type=bool)
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
    
    # Sorting
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Build query
    query = Product.query.filter_by(is_active=True)
    
    # Search filter
    if search:
        search_filter = or_(
            Product.name.contains(search),
            Product.nameAr.contains(search),
            Product.description.contains(search),
            Product.descriptionAr.contains(search),
            Product.short_description.contains(search),
            Product.short_descriptionAr.contains(search),
            Product.sku.contains(search)
        )
        query = query.filter(search_filter)
    
    # Category filter
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Price filters
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Stock filter
    if in_stock is not None:
        if in_stock:
            query = query.filter(Product.stock_quantity > 0)
        else:
            query = query.filter(Product.stock_quantity == 0)
    
    # Featured filter
    if featured is not None:
        query = query.filter_by(is_featured=featured)
    
    # Tags filter
    if tags and tags[0]:  # Check if tags list is not empty
        for tag in tags:
            query = query.filter(Product.tags.any(Tag.name == tag.strip()))
    
    # Sorting
    if sort_by == 'price':
        if sort_order == 'desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.price.asc())
    elif sort_by == 'name':
        if sort_order == 'desc':
            query = query.order_by(Product.name.desc() if Product.nameAr is None else Product.nameAr.desc())
        else:
            query = query.order_by(Product.name.asc()  if Product.nameAr is None else Product.nameAr.asc())
    else:  # created_at or default
        if sort_order == 'desc':
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.created_at.asc())
    
    # Paginate
    products = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    schema = ProductListSchema()
    return jsonify({
        'message': 'Products retrieved successfully',
        'data': schema.dump(products.items, many=True),
        'pagination': {
            'page': products.page,
            'pages': products.pages,
            'per_page': products.per_page,
            'total': products.total,
            'has_next': products.has_next,
            'has_prev': products.has_prev
        },
        'filters': {
            'search': search,
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'in_stock': in_stock,
            'featured': featured,
            'tags': tags
        }
    }), 200

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    schema = ProductDetailSchema()
    return jsonify({
        'message': 'Product retrieved successfully',
        'data': schema.dump(product)
    }), 200

@bp.route('/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """Get product by slug"""
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    schema = ProductDetailSchema()
    return jsonify({
        'message': 'Product retrieved successfully',
        'data': schema.dump(product)
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
@require_admin()
def create_product():
    """Create new product (Admin only)"""
    schema = ProductCreateSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400

    # Generate slug if not provided
    if not data.get('slug'):
        data['slug'] = generate_slug(data['name'])

    # Ensure slug is unique
    base_slug = data['slug']
    existing_product = Product.query.filter_by(slug=data['slug']).first()
    counter = 1
    while existing_product:
        data['slug'] = f"{base_slug}-{counter}"
        existing_product = Product.query.filter_by(slug=data['slug']).first()
        counter += 1

    # Optional ID check
    if 'id' in data:
        if Product.query.get(data['id']):
            return jsonify({'error': 'Product ID already exists'}), 400

    # Handle tags
    tag_names = data.pop('tags', [])

    # Create product (with or without ID)
    product = Product(**data)

    # Attach tags
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name.strip()).first()
        if not tag:
            tag = Tag(name=tag_name.strip())
            db.session.add(tag)
        product.tags.append(tag)

    try:
        db.session.add(product)
        db.session.commit()

        detail_schema = ProductDetailSchema()
        return jsonify({
            'message': 'Product created successfully',
            'data': detail_schema.dump(product)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create product', 'details': str(e)}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_product(product_id):
    """Update product (Admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    schema = ProductUpdateSchema(context={'product_id': product_id})
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Handle slug update

    if 'name' in data and 'slug' not in data:
        new_slug = generate_slug(data['name'])
        existing_product = Product.query.filter_by(slug=new_slug).first()
        if not existing_product or existing_product.id == product_id:
            data['slug'] = new_slug
    
    # Handle tags
    tag_names = data.pop('tags', None)
    
    # Update product fields
    for field, value in data.items():
        if hasattr(product, field):
            setattr(product, field, value)
    
    # Update tags if provided
    if tag_names is not None:
        product.tags.clear()
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if not tag:
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            product.tags.append(tag)
    
    product.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        schema = ProductDetailSchema()
        return jsonify({
            'message': 'Product updated successfully',
            'data': schema.dump(product)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update product', 'details': str(e)}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_product(product_id):
    """Delete product (Admin only) - Soft delete"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Soft delete - set as inactive
    product.is_active = False
    product.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete product', 'details': str(e)}), 500

@bp.route('/<int:product_id>/stock', methods=['PUT'])
@jwt_required()
@require_admin()
def update_stock(product_id):
    """Update product stock (Admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    new_stock = data.get('stock_quantity')
    
    if new_stock is None or new_stock < 0:
        return jsonify({'error': 'Invalid stock quantity'}), 400
    
    product.stock_quantity = new_stock
    product.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Stock updated successfully',
            'data': {
                'product_id': product.id,
                'stock_quantity': product.stock_quantity,
                'is_in_stock': product.is_in_stock(),
                'is_low_stock': product.is_low_stock()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update stock', 'details': str(e)}), 500

@bp.route('/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)  # Max 50 products
    
    products = Product.query.filter_by(
        is_active=True, 
        is_featured=True
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
    schema = ProductListSchema()
    return jsonify({
        'message': 'Featured products retrieved successfully',
        'data': schema.dump(products, many=True)
    }), 200

@bp.route('/search', methods=['GET'])
def search_products():
    """Advanced product search"""
    query_text = request.args.get('q', '').strip()
    
    if not query_text:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Search in multiple fields
    search_filter = or_(
        Product.name.contains(query_text),
        Product.nameAr.contains(query_text),
        Product.description.contains(query_text),
        Product.descriptionAr.contains(query_text),
        Product.short_description.contains(query_text),
        Product.short_descriptionAr.contains(query_text),
        Product.sku.contains(query_text),
        Product.tags.any(Tag.name.contains(query_text))
    )
    
    products = Product.query.filter(
        and_(Product.is_active == True, search_filter)
    ).order_by(Product.created_at.desc()).limit(20).all()
    
    schema = ProductListSchema()
    return jsonify({
        'message': 'Search completed successfully',
        'data': schema.dump(products, many=True),
        'query': query_text,
        'count': len(products)
    }), 200
