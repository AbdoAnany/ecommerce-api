from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc
from app.admin import bp
from app.models import (
    User, Product, Order, OrderItem, Category, 
    UserRole, OrderStatus, PaymentStatus
)
from app import db

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

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin()
def get_dashboard():
    """Get admin dashboard metrics"""
    
    # Date ranges
    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Basic counts
    total_users = User.query.count()
    total_products = Product.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    total_categories = Category.query.filter_by(is_active=True).count()
    
    # Revenue metrics
    total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # Today's metrics
    today_orders = Order.query.filter(
        func.date(Order.created_at) == today
    ).count()
    
    today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # This month's metrics
    month_orders = Order.query.filter(
        func.date(Order.created_at) >= this_month
    ).count()
    
    month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) >= this_month,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).scalar() or 0
    
    # Order status distribution
    order_status_stats = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    # Top selling products
    top_products = db.session.query(
        OrderItem.product_id,
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.total_price).label('total_revenue')
    ).join(Order).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).group_by(
        OrderItem.product_id, OrderItem.product_name
    ).order_by(
        desc(func.sum(OrderItem.quantity))
    ).limit(10).all()
    
    # Recent orders
    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    # Low stock products
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.low_stock_threshold
    ).order_by(Product.stock_quantity.asc()).limit(10).all()
    
    # New users this month
    new_users_count = User.query.filter(
        func.date(User.created_at) >= this_month
    ).count()
    
    dashboard_data = {
        'overview': {
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_categories': total_categories,
            'total_revenue': float(total_revenue),
            'new_users_this_month': new_users_count
        },
        'today': {
            'orders': today_orders,
            'revenue': float(today_revenue)
        },
        'this_month': {
            'orders': month_orders,
            'revenue': float(month_revenue)
        },
        'order_status_distribution': [
            {
                'status': status.value,
                'count': count
            }
            for status, count in order_status_stats
        ],
        'top_selling_products': [
            {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'total_sold': product.total_sold,
                'total_revenue': float(product.total_revenue)
            }
            for product in top_products
        ],
        'recent_orders': [
            {
                'id': order.id,
                'order_number': order.order_number,
                'user_id': order.user_id,
                'customer_name': order.user.get_full_name() if order.user else 'Guest',
                'status': order.status.value,
                'total_amount': float(order.total_amount),
                'created_at': order.created_at.isoformat()
            }
            for order in recent_orders
        ],
        'low_stock_products': [
            {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'stock_quantity': product.stock_quantity,
                'low_stock_threshold': product.low_stock_threshold
            }
            for product in low_stock_products
        ]
    }
    
    return jsonify({
        'message': 'Dashboard data retrieved successfully',
        'data': dashboard_data
    }), 200

@bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin()
def get_users():
    """Get all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)
    search = request.args.get('search', '').strip()
    
    # Build query
    query = User.query
    
    if role:
        query = query.filter_by(role=UserRole(role))
    
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
    
    # Order by created date (newest first)
    query = query.order_by(User.created_at.desc())
    
    users = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    user_list = [
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
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'orders_count': len(user.orders)
        }
        for user in users.items
    ]
    
    return jsonify({
        'message': 'Users retrieved successfully',
        'data': user_list,
        'pagination': {
            'page': users.page,
            'pages': users.pages,
            'per_page': users.per_page,
            'total': users.total,
            'has_next': users.has_next,
            'has_prev': users.has_prev
        }
    }), 200

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_user(user_id):
    """Update user (Admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update allowed fields
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
    
    if 'is_verified' in data:
        user.is_verified = data['is_verified']
    
    user.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'data': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 500

@bp.route('/orders', methods=['GET'])
@jwt_required()
@require_admin()
def get_orders():
    """Get all orders with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query
    query = Order.query
    
    if status:
        try:
            query = query.filter_by(status=OrderStatus(status))
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)
            query = query.filter(Order.created_at >= from_date)
        except ValueError:
            return jsonify({'error': 'Invalid date_from format'}), 400
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to).replace(tzinfo=timezone.utc)
            query = query.filter(Order.created_at <= to_date)
        except ValueError:
            return jsonify({'error': 'Invalid date_to format'}), 400
    
    # Order by created date (newest first)
    query = query.order_by(Order.created_at.desc())
    
    orders = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    order_list = [
        {
            'id': order.id,
            'order_number': order.order_number,
            'user_id': order.user_id,
            'customer_name': order.user.get_full_name() if order.user else 'Guest',
            'customer_email': order.user.email if order.user else None,
            'status': order.status.value,
            'total_amount': float(order.total_amount),
            'currency': order.currency,
            'items_count': order.get_total_items(),
            'payment_status': order.payment.status.value if order.payment else None,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        }
        for order in orders.items
    ]
    
    return jsonify({
        'message': 'Orders retrieved successfully',
        'data': order_list,
        'pagination': {
            'page': orders.page,
            'pages': orders.pages,
            'per_page': orders.per_page,
            'total': orders.total,
            'has_next': orders.has_next,
            'has_prev': orders.has_prev
        }
    }), 200

@bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_order(order_id):
    """Update order status (Admin only)"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update order status
    if 'status' in data:
        try:
            new_status = OrderStatus(data['status'])
            order.status = new_status
            
            # Set timestamps based on status
            if new_status == OrderStatus.SHIPPED:
                order.shipped_at = datetime.now(timezone.utc)
                order.tracking_number = data.get('tracking_number')
            elif new_status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now(timezone.utc)
                if not order.shipped_at:
                    order.shipped_at = datetime.now(timezone.utc)
            
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    
    # Update tracking number
    if 'tracking_number' in data:
        order.tracking_number = data['tracking_number']
    
    # Update notes
    if 'notes' in data:
        order.notes = data['notes']
    
    order.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Order updated successfully',
            'data': {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status.value,
                'tracking_number': order.tracking_number,
                'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update order', 'details': str(e)}), 500

@bp.route('/products/low-stock', methods=['GET'])
@jwt_required()
@require_admin()
def get_low_stock_products():
    """Get products with low stock"""
    threshold = request.args.get('threshold', type=int)
    
    query = Product.query.filter(Product.is_active == True)
    
    if threshold:
        query = query.filter(Product.stock_quantity <= threshold)
    else:
        query = query.filter(Product.stock_quantity <= Product.low_stock_threshold)
    
    products = query.order_by(Product.stock_quantity.asc()).all()
    
    product_list = [
        {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'stock_quantity': product.stock_quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'price': float(product.price),
            'category': product.category.name if product.category else None
        }
        for product in products
    ]
    
    return jsonify({
        'message': 'Low stock products retrieved successfully',
        'data': product_list,
        'count': len(product_list)
    }), 200

@bp.route('/analytics/sales', methods=['GET'])
@jwt_required()
@require_admin()
def get_sales_analytics():
    """Get sales analytics"""
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    
    # Daily sales data
    daily_sales = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        func.date(Order.created_at) >= start_date,
        func.date(Order.created_at) <= end_date,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).group_by(
        func.date(Order.created_at)
    ).order_by(
        func.date(Order.created_at)
    ).all()
    
    # Category sales
    category_sales = db.session.query(
        Category.name.label('category'),
        func.sum(OrderItem.quantity).label('quantity_sold'),
        func.sum(OrderItem.total_price).label('revenue')
    ).join(Product).join(OrderItem).join(Order).filter(
        func.date(Order.created_at) >= start_date,
        Order.status.in_([OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED])
    ).group_by(Category.name).order_by(
        desc(func.sum(OrderItem.total_price))
    ).all()
    
    analytics_data = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'daily_sales': [
            {
                'date': sale.date.isoformat(),
                'orders': sale.orders,
                'revenue': float(sale.revenue or 0)
            }
            for sale in daily_sales
        ],
        'category_sales': [
            {
                'category': sale.category,
                'quantity_sold': sale.quantity_sold,
                'revenue': float(sale.revenue or 0)
            }
            for sale in category_sales
        ]
    }
    
    return jsonify({
        'message': 'Sales analytics retrieved successfully',
        'data': analytics_data
    }), 200

@bp.route('/admin-users', methods=['GET'])
@jwt_required()
@require_admin()
def get_admin_users():
    """Get all admin users"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    is_active = request.args.get('is_active', type=bool)
    search = request.args.get('search', '').strip()
    
    # Build query for admin users only
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
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'orders_count': len(user.orders) if user.orders else 0
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

@bp.route('/current-admin', methods=['GET'])
@jwt_required()
@require_admin()
def get_current_admin():
    """Get current logged-in admin user details"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    return jsonify({
        'message': 'Current admin user retrieved',
        'data': {
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
    }), 200

@bp.route('/admin-stats', methods=['GET'])
@jwt_required()
@require_admin()
def get_admin_stats():
    """Get admin user statistics"""
    total_admins = User.query.filter_by(role=UserRole.ADMIN).count()
    active_admins = User.query.filter_by(role=UserRole.ADMIN, is_active=True).count()
    verified_admins = User.query.filter_by(role=UserRole.ADMIN, is_verified=True).count()
    
    # Get recent admin logins
    recent_admin_logins = User.query.filter(
        User.role == UserRole.ADMIN,
        User.last_login.isnot(None)
    ).order_by(User.last_login.desc()).limit(5).all()
    
    return jsonify({
        'message': 'Admin statistics retrieved',
        'data': {
            'counts': {
                'total_admins': total_admins,
                'active_admins': active_admins,
                'verified_admins': verified_admins
            },
            'recent_logins': [
                {
                    'id': admin.id,
                    'username': admin.username,
                    'email': admin.email,
                    'last_login': admin.last_login.isoformat()
                }
                for admin in recent_admin_logins
            ]
        }
    }), 200

@bp.route('/promote-user/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def promote_user_to_admin(user_id):
    """Promote a user to admin role (Admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is already admin
    if user.role == UserRole.ADMIN:
        return jsonify({
            'message': 'User is already an admin',
            'data': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role.value
            }
        }), 200
    
    try:
        # Store previous role for logging
        previous_role = user.role.value
        
        # Update to admin
        user.role = UserRole.ADMIN
        user.is_active = True  # Ensure admin is active
        user.is_verified = True  # Ensure admin is verified
        user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': f'User promoted to admin successfully',
            'data': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'previous_role': previous_role,
                'new_role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to promote user to admin', 'details': str(e)}), 500

@bp.route('/demote-admin/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def demote_admin_to_user(user_id):
    """Demote an admin to regular user (Admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is admin
    if user.role != UserRole.ADMIN:
        return jsonify({'error': 'User is not an admin'}), 400
    
    # Prevent demoting yourself
    current_user_id = int(get_jwt_identity())
    if user.id == current_user_id:
        return jsonify({'error': 'Cannot demote yourself'}), 400
    
    # Check if this is the last admin
    admin_count = User.query.filter_by(role=UserRole.ADMIN, is_active=True).count()
    if admin_count <= 1:
        return jsonify({'error': 'Cannot demote the last admin user'}), 400
    
    try:
        # Update to customer
        user.role = UserRole.CUSTOMER
        user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Admin demoted to customer successfully',
            'data': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'previous_role': 'admin',
                'new_role': user.role.value,
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to demote admin to user', 'details': str(e)}), 500

@bp.route('/bulk-promote', methods=['POST'])
@jwt_required()
@require_admin()
def bulk_promote_users():
    """Promote multiple users to admin (Admin only)"""
    data = request.get_json()
    
    if not data or 'user_ids' not in data:
        return jsonify({'error': 'user_ids array is required'}), 400
    
    user_ids = data['user_ids']
    
    if not isinstance(user_ids, list) or len(user_ids) == 0:
        return jsonify({'error': 'user_ids must be a non-empty array'}), 400
    
    try:
        promoted_users = []
        errors = []
        
        for user_id in user_ids:
            user = User.query.get(user_id)
            
            if not user:
                errors.append(f"User ID {user_id} not found")
                continue
            
            if user.role == UserRole.ADMIN:
                errors.append(f"User {user.username} (ID: {user_id}) is already admin")
                continue
            
            # Promote to admin
            previous_role = user.role.value
            user.role = UserRole.ADMIN
            user.is_active = True
            user.is_verified = True
            user.updated_at = datetime.now(timezone.utc)
            
            promoted_users.append({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'previous_role': previous_role,
                'new_role': user.role.value
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Bulk promotion completed',
            'promoted_count': len(promoted_users),
            'promoted_users': promoted_users,
            'errors': errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Bulk promotion failed', 'details': str(e)}), 500

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@jwt_required()
@require_admin()
def reset_user_password_admin(user_id):
    """Reset user password (Admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or 'new_password' not in data:
        return jsonify({'error': 'New password is required'}), 400
    
    new_password = data['new_password']
    
    # Validate password length
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    try:
        # Reset password
        user.set_password(new_password)
        user.reset_token = None  # Clear any existing reset token
        user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Password reset successfully for user {user.username}',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password', 'details': str(e)}), 500

@bp.route('/reset-admin-password', methods=['POST'])
@jwt_required()
@require_admin()
def reset_admin_password_endpoint():
    """Reset admin password to default (Super Admin only)"""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    data = request.get_json() or {}
    target_email = data.get('admin_email', 'admin@example.com')
    new_password = data.get('new_password', 'admin123')
    
    # Find the target admin user
    admin_user = User.query.filter_by(email=target_email, role=UserRole.ADMIN).first()
    
    if not admin_user:
        return jsonify({'error': f'Admin user with email {target_email} not found'}), 404
    
    # Don't allow resetting your own password this way (use change password instead)
    if admin_user.id == current_user_id:
        return jsonify({'error': 'Use change password endpoint to update your own password'}), 400
    
    try:
        admin_user.set_password(new_password)
        admin_user.reset_token = None
        admin_user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Admin password reset successfully for {admin_user.email}',
            'admin': {
                'id': admin_user.id,
                'email': admin_user.email,
                'username': admin_user.username
            },
            'warning': 'Admin should change this password after next login'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset admin password', 'details': str(e)}), 500

@bp.route('/change-password', methods=['POST'])
@jwt_required()
@require_admin()
def change_admin_password():
    """Change current admin password"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Validate new password
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    
    if current_password == new_password:
        return jsonify({'error': 'New password must be different from current password'}), 400
    
    try:
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@bp.route('/generate-password', methods=['GET'])
@jwt_required()
@require_admin()
def generate_secure_password_endpoint():
    """Generate a secure password"""
    import secrets
    import string
    
    # Generate a 12-character password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    return jsonify({
        'message': 'Secure password generated',
        'password': password,
        'length': len(password),
        'note': 'Use this password with password reset endpoints'
    }), 200
