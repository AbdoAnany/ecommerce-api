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
    # Handle multilingual text - use English if available, otherwise first available language
    if isinstance(text, dict):
        slug_text = text.get('en', next(iter(text.values())) if text else '')
    else:
        slug_text = text
    
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', str(slug_text)).strip()
    slug = re.sub(r'[\s_-]+', '-', slug).lower()
    return slug

def search_multilingual_field(field, search_term):
    """Helper function to search in multilingual fields"""
    # For PostgreSQL with JSON fields
    if hasattr(field, 'astext'):
        return or_(
            field['en'].astext.ilike(f'%{search_term}%'),
            field['ar'].astext.ilike(f'%{search_term}%')
        )
    # For MySQL with JSON fields
    elif hasattr(field, 'op'):
        return or_(
            field.op('JSON_EXTRACT')(field, '$.en').like(f'%{search_term}%'),
            field.op('JSON_EXTRACT')(field, '$.ar').like(f'%{search_term}%')
        )
    # Fallback for other databases or text fields
    else:
        return field.ilike(f'%{search_term}%')

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
    
    # Search filter - updated for multilingual fields
    if search:
        search_filter = or_(
            search_multilingual_field(Product.name, search),
            search_multilingual_field(Product.description, search),
            search_multilingual_field(Product.short_description, search),
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
    
    # Sorting - updated for multilingual name field
    if sort_by == 'price':
        if sort_order == 'desc':
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Product.price.asc())
    elif sort_by == 'name':
        # Sort by English name if available, otherwise by the JSON field
        if sort_order == 'desc':
            query = query.order_by(Product.name['en'].astext.desc())
        else:
            query = query.order_by(Product.name['en'].astext.asc())
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
    
    # Check if slug already exists
    existing_product = Product.query.filter_by(slug=data['slug']).first()
    if existing_product:
        # Generate unique slug
        base_slug = data['slug']
        counter = 1
        while existing_product:
            data['slug'] = f"{base_slug}-{counter}"
            existing_product = Product.query.filter_by(slug=data['slug']).first()
            counter += 1
    
    # Handle tags
    tag_names = data.pop('tags', [])
    
    # Handle image URLs - extract from data if present
    image_urls = data.pop('image_urls', [])
    
    # Create product
    product = Product(**data)
    
    # Add tags
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if not tag:
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            product.tags.append(tag)
    
    # Handle image URLs if provided
    if image_urls:
        from app.models import ProductImage  # Import here to avoid circular imports
        
        for idx, image_url in enumerate(image_urls):
            # Validate URL format (basic validation)
            if not image_url.startswith(('http://', 'https://')):
                continue
                
            # Create ProductImage record
            product_image = ProductImage(
                product=product,
                url=image_url,
                alt_text=f"Product image {idx + 1}",
                is_primary=(idx == 0),  # First image is primary
                sort_order=idx
            )
            db.session.add(product_image)
    
    try:
        db.session.add(product)
        db.session.commit()
        
        schema = ProductDetailSchema()
        return jsonify({
            'message': 'Product created successfully',
            'data': schema.dump(product)
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
    
    # Handle image URLs
    image_urls = data.pop('image_urls', None)
    
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
    
    # Handle image URLs if provided
    if image_urls is not None:
        from app.models import ProductImage  # Import here to avoid circular imports
        
        # Remove existing images
        ProductImage.query.filter_by(product_id=product.id).delete()
        
        # Add new images
        for idx, image_url in enumerate(image_urls):
            # Validate URL format (basic validation)
            if not image_url.startswith(('http://', 'https://')):
                continue
                
            # Create ProductImage record
            product_image = ProductImage(
                product_id=product.id,
                url=image_url,
                alt_text=f"Product image {idx + 1}",
                is_primary=(idx == 0),  # First image is primary
                sort_order=idx
            )
            db.session.add(product_image)
    
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
    
    # Search in multiple fields including multilingual fields
    search_filter = or_(
        search_multilingual_field(Product.name, query_text),
        search_multilingual_field(Product.description, query_text),
        search_multilingual_field(Product.short_description, query_text),
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

@bp.route('/<int:product_id>/images', methods=['POST'])
@jwt_required()
@require_admin()
def add_product_images(product_id):
    """Add images to product (Admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    image_urls = data.get('image_urls', [])
    
    if not image_urls:
        return jsonify({'error': 'Image URLs are required'}), 400
    
    try:
        from app.models import ProductImage
        
        # Get current max sort order
        max_sort = db.session.query(db.func.max(ProductImage.sort_order)).filter_by(product_id=product_id).scalar() or -1
        
        added_images = []
        for idx, image_url in enumerate(image_urls):
            # Validate URL format
            if not image_url.startswith(('http://', 'https://')):
                continue
                
            # Create ProductImage record
            product_image = ProductImage(
                product_id=product_id,
                url=image_url,
                alt_text=data.get('alt_text', f"Product image {max_sort + idx + 2}"),
                is_primary=False,  # Don't change primary image when adding
                sort_order=max_sort + idx + 1
            )
            db.session.add(product_image)
            added_images.append({
                'url': image_url,
                'sort_order': max_sort + idx + 1
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully added {len(added_images)} images',
            'data': added_images
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add images', 'details': str(e)}), 500

@bp.route('/<int:product_id>/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_product_image(product_id, image_id):
    """Delete product image (Admin only)"""
    from app.models import ProductImage
    
    product_image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
    
    if not product_image:
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        was_primary = product_image.is_primary
        db.session.delete(product_image)
        
        # If deleted image was primary, make first remaining image primary
        if was_primary:
            new_primary = ProductImage.query.filter_by(product_id=product_id).order_by(ProductImage.sort_order).first()
            if new_primary:
                new_primary.is_primary = True
        
        db.session.commit()
        
        return jsonify({'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete image', 'details': str(e)}), 500

@bp.route('/<int:product_id>/images/<int:image_id>/primary', methods=['PUT'])
@jwt_required()
@require_admin()
def set_primary_image(product_id, image_id):
    """Set primary image for product (Admin only)"""
    from app.models import ProductImage
    
    product_image = ProductImage.query.filter_by(id=image_id, product_id=product_id).first()
    
    if not product_image:
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        # Remove primary flag from all images of this product
        ProductImage.query.filter_by(product_id=product_id).update({'is_primary': False})
        
        # Set this image as primary
        product_image.is_primary = True
        
        db.session.commit()
        
        return jsonify({'message': 'Primary image updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update primary image', 'details': str(e)}), 500
@jwt_required()
@require_admin()
def bulk_update_products():
    """Bulk update products (Admin only)"""
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    updates = data.get('updates', {})
    
    if not product_ids or not updates:
        return jsonify({'error': 'Product IDs and updates are required'}), 400
    
    # Validate updates
    allowed_fields = ['is_active', 'is_featured', 'category_id', 'stock_quantity']
    invalid_fields = [field for field in updates.keys() if field not in allowed_fields]
    
    if invalid_fields:
        return jsonify({'error': f'Invalid fields for bulk update: {invalid_fields}'}), 400
    
    try:
        # Update products
        updated_count = Product.query.filter(Product.id.in_(product_ids)).update(
            updates, synchronize_session=False
        )
        
        # Update timestamps
        Product.query.filter(Product.id.in_(product_ids)).update(
            {'updated_at': datetime.now(timezone.utc)}, synchronize_session=False
        )
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully updated {updated_count} products',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to bulk update products', 'details': str(e)}), 500