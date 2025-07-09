from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app.users import bp
from app.users.schemas import UpdateUserSchema, UserProfileSchema, UserListSchema
from app.models import User, Order, OrderItem
from app import db

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = UserProfileSchema()
    return jsonify({
        'message': 'Profile retrieved successfully',
        'data': schema.dump(user)
    }), 200

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = UpdateUserSchema(context={'user_id': user_id})
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Update user fields
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        profile_schema = UserProfileSchema()
        return jsonify({
            'message': 'Profile updated successfully',
            'data': profile_schema.dump(user)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get current user's order history"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    status = request.args.get('status')
    
    # Build query
    query = Order.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by newest first
    query = query.order_by(Order.created_at.desc())
    
    # Paginate
    orders = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Format orders
    order_list = []
    for order in orders.items:
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status.value,
            'total_amount': float(order.total_amount),
            'currency': order.currency,
            'created_at': order.created_at.isoformat(),
            'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            'items_count': order.get_total_items(),
            'items': [
                {
                    'id': item.id,
                    'product_name': item.product_name,
                    'product_sku': item.product_sku,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price)
                }
                for item in order.items
            ]
        }
        order_list.append(order_data)
    
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

@bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_user_order(order_id):
    """Get specific order details for current user"""
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    order_data = {
        'id': order.id,
        'order_number': order.order_number,
        'status': order.status.value,
        'subtotal': float(order.subtotal),
        'tax_amount': float(order.tax_amount),
        'shipping_amount': float(order.shipping_amount),
        'discount_amount': float(order.discount_amount),
        'total_amount': float(order.total_amount),
        'currency': order.currency,
        'shipping_address': order.shipping_address,
        'billing_address': order.billing_address,
        'tracking_number': order.tracking_number,
        'notes': order.notes,
        'created_at': order.created_at.isoformat(),
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        'items': [
            {
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_sku': item.product_sku,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price)
            }
            for item in order.items
        ],
        'payment': {
            'method': order.payment.payment_method,
            'status': order.payment.status.value,
            'amount': float(order.payment.amount)
        } if order.payment else None
    }
    
    return jsonify({
        'message': 'Order retrieved successfully',
        'data': order_data
    }), 200

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    """Get user dashboard summary"""
    user_id = int(get_jwt_identity())
    
    # Get order statistics
    total_orders = Order.query.filter_by(user_id=user_id).count()
    completed_orders = Order.query.filter_by(user_id=user_id, status='delivered').count()
    pending_orders = Order.query.filter_by(user_id=user_id, status='pending').count()
    
    # Get total spent
    total_spent = db.session.query(db.func.sum(Order.total_amount)).filter_by(
        user_id=user_id
    ).scalar() or 0
    
    # Get recent orders
    recent_orders = Order.query.filter_by(user_id=user_id).order_by(
        Order.created_at.desc()
    ).limit(5).all()
    
    # Get favorite products (most ordered)
    favorite_products = db.session.query(
        OrderItem.product_id,
        OrderItem.product_name,
        db.func.sum(OrderItem.quantity).label('total_quantity')
    ).join(Order).filter(
        Order.user_id == user_id
    ).group_by(
        OrderItem.product_id, OrderItem.product_name
    ).order_by(
        db.func.sum(OrderItem.quantity).desc()
    ).limit(5).all()
    
    dashboard_data = {
        'stats': {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_spent': float(total_spent)
        },
        'recent_orders': [
            {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status.value,
                'total_amount': float(order.total_amount),
                'created_at': order.created_at.isoformat()
            }
            for order in recent_orders
        ],
        'favorite_products': [
            {
                'product_id': item.product_id,
                'product_name': item.product_name,
                'total_quantity': item.total_quantity
            }
            for item in favorite_products
        ]
    }
    
    return jsonify({
        'message': 'Dashboard data retrieved successfully',
        'data': dashboard_data
    }), 200
