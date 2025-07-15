from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from app.categories import bp
from app.models import Category, User, UserRole
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
def get_categories():
    """Get all active categories"""
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order, Category.name).all()
    category_list = []
    for category in categories:
        # Get language preference from query parameter, default to English
        lang = request.args.get('lang', 'en')
        
        category_data = {
            'id': category.id,
            'name': category.get_name(lang),
            'name_all': category.name,  # Return all translations
            'description': category.get_description(lang),
            'description_all': category.description,  # Return all translations
            'slug': category.slug,
            'image_url': category.image_url,
            'sort_order': category.sort_order,
            'parent_id': category.parent_id,
            'product_count': len(category.products),
            'children': [
                {
                    'id': child.id,
                    'name': child.get_name(lang),
                    'name_all': child.name,
                    'slug': child.slug,
                    'product_count': len(child.products)
                }
                for child in category.children if child.is_active
            ]
        }
        category_list.append(category_data)
    return jsonify({
        'message': 'Categories retrieved successfully',
        'data': category_list
    }), 200


@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    category = Category.query.filter_by(id=category_id, is_active=True).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Get language preference from query parameter, default to English
    lang = request.args.get('lang', 'en')
    
    category_data = {
        'id': category.id,
        'name': category.get_name(lang),
        'name_all': category.name,  # Return all translations
        'description': category.get_description(lang),
        'description_all': category.description,  # Return all translations
        'slug': category.slug,
        'image_url': category.image_url,
        'sort_order': category.sort_order,
        'parent_id': category.parent_id,
        'parent': {
            'id': category.parent.id,
            'name': category.parent.get_name(lang),
            'name_all': category.parent.name,
            'slug': category.parent.slug
        } if category.parent else None,
        'children': [
            {
                'id': child.id,
                'name': child.get_name(lang),
                'name_all': child.name,
                'slug': child.slug,
                'description': child.get_description(lang),
                'description_all': child.description,
                'product_count': len(child.products)
            }
            for child in category.children if child.is_active
        ],
        'product_count': len(category.products),
        'created_at': category.created_at.isoformat() if category.created_at else None,
        'updated_at': category.updated_at.isoformat() if category.updated_at else None
    }

    return jsonify({
        'message': 'Category retrieved successfully',
        'data': category_data
    }), 200


@bp.route('/slug/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """Get category by slug"""
    category = Category.query.filter_by(slug=slug, is_active=True).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Get language preference from query parameter, default to English
    lang = request.args.get('lang', 'en')
    
    category_data = {
        'id': category.id,
        'name': category.get_name(lang),
        'name_all': category.name,  # Return all translations
        'description': category.get_description(lang),
        'description_all': category.description,  # Return all translations
        'slug': category.slug,
        'image_url': category.image_url,
        'sort_order': category.sort_order,
        'parent_id': category.parent_id,
        'parent': {
            'id': category.parent.id,
            'name': category.parent.get_name(lang),
            'name_all': category.parent.name,
            'slug': category.parent.slug
        } if category.parent else None,
        'children': [
            {
                'id': child.id,
                'name': child.get_name(lang),
                'name_all': child.name,
                'slug': child.slug,
                'description': child.get_description(lang),
                'description_all': child.description,
                'product_count': len(child.products)
            }
            for child in category.children if child.is_active
        ],
        'product_count': len(category.products)
    }

    return jsonify({
        'message': 'Category retrieved successfully',
        'data': category_data
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@require_admin()
def create_category():
    """Create new category (Admin only)"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400

    slug = data.get('slug') or generate_slug(data['name'])

    existing_category = Category.query.filter_by(slug=slug).first()
    if existing_category:
        base_slug = slug
        counter = 1
        while existing_category:
            slug = f"{base_slug}-{counter}"
            existing_category = Category.query.filter_by(slug=slug).first()
            counter += 1

    parent_id = data.get('parent_id')
    if parent_id:
        parent_category = Category.query.get(parent_id)
        if not parent_category:
            return jsonify({'error': 'Parent category not found'}), 400

    # Handle multilingual fields
    name_data = {
        'en': data['name'],
        'ar': data.get('name_ar', data['name'])
    }
    description_data = None
    if 'description' in data or 'description_ar' in data:
        description_data = {
            'en': data.get('description', ''),
            'ar': data.get('description_ar', data.get('description', ''))
        }

    category = Category(
        name=name_data,
        description=description_data,
        slug=slug,
        image_url=data.get('image_url'),
        sort_order=data.get('sort_order', 0),
        parent_id=parent_id,
        is_active=data.get('is_active', True)
    )

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify({
            'message': 'Category created successfully',
            'data': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
                'is_active': category.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create category', 'details': str(e)}), 500


@bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_category(category_id):
    """Update category (Admin only)"""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Handle multilingual name update
    if 'name' in data or 'name_ar' in data:
        current_name = category.name if isinstance(category.name, dict) else {'en': category.name, 'ar': category.name}
        name_data = {
            'en': data.get('name', current_name['en']),
            'ar': data.get('name_ar', current_name['ar'])
        }
        category.name = name_data
        # Update slug based on English name if not provided
        if 'slug' not in data:
            new_slug = generate_slug(name_data['en'])
            existing_category = Category.query.filter_by(slug=new_slug).first()
            if not existing_category or existing_category.id == category_id:
                category.slug = new_slug

    # Handle multilingual description update
    if 'description' in data or 'description_ar' in data:
        current_desc = category.description if isinstance(category.description, dict) else {'en': category.description, 'ar': category.description}
        description_data = {
            'en': data.get('description', current_desc.get('en', '')),
            'ar': data.get('description_ar', current_desc.get('ar', ''))
        }
        category.description = description_data

    if 'slug' in data:
        category.slug = data['slug']

    if 'image_url' in data:
        category.image_url = data['image_url']

    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    if 'parent_id' in data:
        parent_id = data['parent_id']
        if parent_id and parent_id != category_id:
            parent_category = Category.query.get(parent_id)
            if not parent_category:
                return jsonify({'error': 'Parent category not found'}), 400
        category.parent_id = parent_id

    if 'is_active' in data:
        category.is_active = data['is_active']

    category.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({
            'message': 'Category updated successfully',
            'data': {
                'id': category.id,
                'name': category.name,
                'name_alt': category.name_alt,
                'slug': category.slug,
                'description': category.description,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
                'thumbnail': category.thumbnail,
                'is_active': category.is_active
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update category', 'details': str(e)}), 500


@bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_category(category_id):
    """Delete category (Admin only) - Soft delete"""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    if category.products:
        return jsonify({'error': 'Cannot delete category with products. Move products first.'}), 400

    if category.children:
        return jsonify({'error': 'Cannot delete category with subcategories. Delete subcategories first.'}), 400

    category.is_active = False
    category.updated_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete category', 'details': str(e)}), 500


@bp.route('/tree', methods=['GET'])
def get_category_tree():
    """Get hierarchical category tree"""
    root_categories = Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.sort_order, Category.name).all()

    def build_tree(categories):
        tree = []
        # Get language preference from query parameter, default to English
        lang = request.args.get('lang', 'en')
        
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.get_name(lang),
                'name_all': category.name,  # Return all translations
                'slug': category.slug,
                'description': category.get_description(lang),
                'description_all': category.description,  # Return all translations
                'image_url': category.image_url,
                'sort_order': category.sort_order,
                'product_count': len(category.products),
                'children': build_tree([child for child in category.children if child.is_active])
            }
            tree.append(category_data)
        return tree

    tree = build_tree(root_categories)
    return jsonify({
        'message': 'Category tree retrieved successfully',
        'data': tree
    }), 200