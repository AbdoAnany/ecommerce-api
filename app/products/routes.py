from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from sqlalchemy import or_, and_
from app.products import bp
from app.products.schemas import (
    ProductCreateSchema, ProductUpdateSchema,
    ProductListSchema, ProductDetailSchema
)
from app.models import Product, Category, Tag, User, UserRole, Image
from app import db
import re

def require_admin():
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
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip()
    slug = re.sub(r'[\s_-]+', '-', slug).lower()
    return slug

def build_product_query(args):
    query = Product.query.filter_by(is_active=True)

    search = args.get('search', '').strip()
    category_id = args.get('category_id', type=int)
    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)
    in_stock = args.get('in_stock', type=bool)
    featured = args.get('featured', type=bool)
    tags = args.get('tags', '').split(',') if args.get('tags') else []

    if search:
        query = query.filter(or_(
            Product.name.contains(search),
            Product.nameAr.contains(search),
            Product.description.contains(search),
            Product.descriptionAr.contains(search),
            Product.short_description.contains(search),
            Product.short_descriptionAr.contains(search),
            Product.sku.contains(search)
        ))

    if category_id:
        query = query.filter_by(category_id=category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if in_stock is not None:
        query = query.filter(Product.stock_quantity > 0 if in_stock else Product.stock_quantity == 0)

    if featured is not None:
        query = query.filter_by(is_featured=featured)

    if tags and tags[0]:
        for tag in tags:
            query = query.filter(Product.tags.any(Tag.name == tag.strip()))

    return query

@bp.route('', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = min(
        request.args.get('per_page', current_app.config['DEFAULT_PAGE_SIZE'], type=int),
        current_app.config['MAX_PAGE_SIZE']
    )

    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    query = build_product_query(request.args)

    if sort_by == 'price':
        query = query.order_by(Product.price.desc() if sort_order == 'desc' else Product.price.asc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.desc() if sort_order == 'desc' else Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc() if sort_order == 'desc' else Product.created_at.asc())

    products = query.paginate(page=page, per_page=per_page, error_out=False)
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
        'filters': {key: request.args.get(key) for key in [
            'search', 'category_id', 'min_price', 'max_price', 'in_stock', 'featured', 'tags'
        ]}
    }), 200

@bp.route('/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    args = request.args.to_dict(flat=True)
    args['category_id'] = category_id
    return get_products()

@bp.route('/featured', methods=['GET'])
def get_featured_products():
    args = request.args.to_dict(flat=True)
    args['featured'] = 'true'
    return get_products()

@bp.route('/search', methods=['GET'])
def search_products():
    query_text = request.args.get('q', '').strip()
    if not query_text:
        return jsonify({'error': 'Search query is required'}), 400

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

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    schema = ProductDetailSchema()
    return jsonify({'message': 'Product retrieved successfully', 'data': schema.dump(product)}), 200

@bp.route('/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    schema = ProductDetailSchema()
    return jsonify({'message': 'Product retrieved successfully', 'data': schema.dump(product)}), 200

@bp.route('', methods=['POST'])
@jwt_required()
@require_admin()
def create_product():
    schema = ProductCreateSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400

    if not data.get('slug'):
        data['slug'] = generate_slug(data['name'])

    base_slug = data['slug']
    counter = 1
    while Product.query.filter_by(slug=data['slug']).first():
        data['slug'] = f"{base_slug}-{counter}"
        counter += 1

    if 'id' in data and Product.query.get(data['id']):
        return jsonify({'error': 'Product ID already exists'}), 400

    tag_names = data.pop('tags', [])
    product = Product(**data)

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
        return jsonify({'message': 'Product created successfully', 'data': detail_schema.dump(product)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create product', 'details': str(e)}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    schema = ProductUpdateSchema(context={'product_id': product_id})
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400

    if 'name' in data and 'slug' not in data:
        new_slug = generate_slug(data['name'])
        if not Product.query.filter_by(slug=new_slug).first() or new_slug == product.slug:
            data['slug'] = new_slug

    tag_names = data.pop('tags', None)
    images_data = data.pop('images', None)

    for field, value in data.items():
        if hasattr(product, field):
            setattr(product, field, value)

    if tag_names is not None:
        product.tags.clear()
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name.strip()).first()
            if not tag:
                tag = Tag(name=tag_name.strip())
                db.session.add(tag)
            product.tags.append(tag)

    if images_data is not None:
        product.images.clear()
        for img in images_data:
            new_image = Image(url=img['url'], alt=img.get('alt', ''))
            product.images.append(new_image)

    product.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        schema = ProductDetailSchema()
        return jsonify({'message': 'Product updated successfully', 'data': schema.dump(product)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update product', 'details': str(e)}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

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
