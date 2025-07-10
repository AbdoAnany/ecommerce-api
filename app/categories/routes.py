from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from app.categories import bp
from app.categories.schemas import (
    CategoryCreateSchema, CategoryUpdateSchema, 
    CategoryListSchema, CategoryDetailSchema, CategoryTreeSchema
)
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
    tree = request.args.get('tree', type=bool, default=False)
    featured_only = request.args.get('featured', type=bool, default=False)
    parent_id = request.args.get('parent_id', type=int)
    
    query = Category.query.filter_by(is_active=True)
    
    if featured_only:
        query = query.filter_by(is_featured=True)
    
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    elif tree:
        # For tree view, get only root categories (no parent)
        query = query.filter_by(parent_id=None)
    
    categories = query.order_by(Category.position, Category.name_en).all()
    
    if tree:
        schema = CategoryTreeSchema(many=True)
    else:
        schema = CategoryListSchema(many=True)
    
    return jsonify({
        'message': 'Categories retrieved successfully',
        'data': schema.dump(categories)
    }), 200

@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    category = Category.query.filter_by(id=category_id, is_active=True).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    schema = CategoryDetailSchema()
    return jsonify({
        'message': 'Category retrieved successfully',
        'data': schema.dump(category)
    }), 200

@bp.route('/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """Get category by slug"""
    category = Category.query.filter(
        db.or_(Category.slug == slug, Category.slug_en == slug, Category.slug_ar == slug),
        Category.is_active == True
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    schema = CategoryDetailSchema()
    return jsonify({
        'message': 'Category retrieved successfully',
        'data': schema.dump(category)
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
@require_admin()
def create_category():
    """Create new category (Admin only)"""
    schema = CategoryCreateSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Generate slugs if not provided
    if not data.get('slug'):
        data['slug'] = generate_slug(data['name_en'])
    if not data.get('slug_en'):
        data['slug_en'] = generate_slug(data['name_en'])
    if not data.get('slug_ar') and data.get('name_ar'):
        data['slug_ar'] = generate_slug(data['name_ar'])
    
    # Check if primary slug already exists
    existing_category = Category.query.filter_by(slug=data['slug']).first()
    if existing_category:
        base_slug = data['slug']
        counter = 1
        while existing_category:
            data['slug'] = f"{base_slug}-{counter}"
            existing_category = Category.query.filter_by(slug=data['slug']).first()
            counter += 1
    
    # Create category
    category = Category(**data)
    
    try:
        db.session.add(category)
        db.session.commit()
        
        schema = CategoryDetailSchema()
        return jsonify({
            'message': 'Category created successfully',
            'data': schema.dump(category)
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
    
    # Update fields
    if 'name' in data:
        category.name = data['name']
        # Generate new slug if name changed and slug not provided
        if 'slug' not in data:
            new_slug = generate_slug(data['name'])
            existing_category = Category.query.filter_by(slug=new_slug).first()
            if not existing_category or existing_category.id == category_id:
                category.slug = new_slug
    
    if 'description' in data:
        category.description = data['description']
    
    if 'slug' in data:
        category.slug = data['slug']
    
    if 'image_url' in data:
        category.image_url = data['image_url']
    
    if 'sort_order' in data:
        category.sort_order = data['sort_order']
    
    if 'parent_id' in data:
        parent_id = data['parent_id']
        if parent_id and parent_id != category_id:  # Prevent self-reference
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
                'slug': category.slug,
                'description': category.description,
                'parent_id': category.parent_id,
                'sort_order': category.sort_order,
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
    
    # Check if category has products
    if category.products:
        return jsonify({'error': 'Cannot delete category with products. Move products first.'}), 400
    
    # Check if category has child categories
    if category.children:
        return jsonify({'error': 'Cannot delete category with subcategories. Delete subcategories first.'}), 400
    
    # Soft delete - set as inactive
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
    # Get root categories (no parent)
    root_categories = Category.query.filter_by(parent_id=None, is_active=True).order_by(Category.sort_order, Category.name).all()
    
    def build_tree(categories):
        tree = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
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
