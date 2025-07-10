#!/usr/bin/env python3
"""
Examples of how to get/retrieve admin users in the e-commerce API
"""

from app.models import User, UserRole
from app import db
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# =============================================================================
# DATABASE QUERY METHODS
# =============================================================================

def get_admin_user_by_email(email):
    """Get admin user by email"""
    return User.query.filter_by(
        email=email, 
        role=UserRole.ADMIN
    ).first()

def get_admin_user_by_id(user_id):
    """Get admin user by ID"""
    return User.query.filter_by(
        id=user_id, 
        role=UserRole.ADMIN
    ).first()

def get_all_admin_users():
    """Get all admin users"""
    return User.query.filter_by(role=UserRole.ADMIN).all()

def get_active_admin_users():
    """Get only active admin users"""
    return User.query.filter_by(
        role=UserRole.ADMIN, 
        is_active=True
    ).all()

def search_admin_users(search_term):
    """Search admin users by name, email, or username"""
    return User.query.filter(
        User.role == UserRole.ADMIN,
        db.or_(
            User.email.contains(search_term),
            User.username.contains(search_term),
            User.first_name.contains(search_term),
            User.last_name.contains(search_term)
        )
    ).all()

def get_admin_with_login_info():
    """Get admin users with last login info"""
    return User.query.filter(
        User.role == UserRole.ADMIN,
        User.last_login.isnot(None)
    ).order_by(User.last_login.desc()).all()

# =============================================================================
# API ENDPOINT EXAMPLES
# =============================================================================

def get_current_admin_user():
    """Get current logged-in admin user"""
    @jwt_required()
    def _get_current_admin():
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        return jsonify({
            'message': 'Current admin user retrieved',
            'data': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'role': user.role.value,
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
    
    return _get_current_admin()

def get_admin_users_endpoint():
    """API endpoint to get all admin users"""
    @jwt_required()
    def _get_admin_users():
        # Verify current user is admin
        user_id = int(get_jwt_identity())
        current_user = User.query.get(user_id)
        
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        is_active = request.args.get('is_active', type=bool)
        search = request.args.get('search', '').strip()
        
        # Build query for admin users
        query = User.query.filter_by(role=UserRole.ADMIN)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if search:
            search_filter = db.or_(
                User.email.contains(search),
                User.username.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search)
            )
            query = query.filter(search_filter)
        
        # Order by created date
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        admin_users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format response
        admin_list = [
            {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            for user in admin_users.items
        ]
        
        return jsonify({
            'message': 'Admin users retrieved successfully',
            'data': admin_list,
            'pagination': {
                'page': admin_users.page,
                'pages': admin_users.pages,
                'per_page': admin_users.per_page,
                'total': admin_users.total,
                'has_next': admin_users.has_next,
                'has_prev': admin_users.has_prev
            }
        }), 200
    
    return _get_admin_users()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_if_user_is_admin(user_id):
    """Check if a user ID belongs to an admin"""
    user = User.query.get(user_id)
    return user and user.role == UserRole.ADMIN

def get_admin_count():
    """Get total number of admin users"""
    return User.query.filter_by(role=UserRole.ADMIN).count()

def get_active_admin_count():
    """Get number of active admin users"""
    return User.query.filter_by(
        role=UserRole.ADMIN, 
        is_active=True
    ).count()

def admin_user_exists():
    """Check if any admin user exists"""
    return User.query.filter_by(role=UserRole.ADMIN).first() is not None

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Examples of how to use these functions"""
    
    # 1. Get the main admin user
    admin = get_admin_user_by_email('admin@example.com')
    if admin:
        print(f"Admin found: {admin.username} ({admin.email})")
    
    # 2. Get all admin users
    all_admins = get_all_admin_users()
    print(f"Total admin users: {len(all_admins)}")
    
    # 3. Check if admin exists
    if admin_user_exists():
        print("Admin user exists in the system")
    
    # 4. Search for admin users
    search_results = search_admin_users('admin')
    print(f"Found {len(search_results)} admin users matching 'admin'")
    
    # 5. Get active admin count
    active_count = get_active_admin_count()
    print(f"Active admin users: {active_count}")

# =============================================================================
# FLASK ROUTE EXAMPLES (to add to your app)
# =============================================================================

"""
Add these routes to your admin blueprint:

from flask import Blueprint
from app.admin import bp

@bp.route('/admin-users', methods=['GET'])
@jwt_required()
def get_admin_users():
    return get_admin_users_endpoint()

@bp.route('/current-admin', methods=['GET'])
@jwt_required()
def get_current_admin():
    return get_current_admin_user()

@bp.route('/admin-count', methods=['GET'])
@jwt_required()
def get_admin_count_endpoint():
    if not check_if_user_is_admin(int(get_jwt_identity())):
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({
        'total_admins': get_admin_count(),
        'active_admins': get_active_admin_count()
    }), 200
"""
