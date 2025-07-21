from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app.cart import bp
from app.models import Cart, CartItem, Product, User
from app import db

@bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get current user's cart"""
    user_id = int(get_jwt_identity())
    
    # Get or create cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    
    # Format cart data
    cart_data = {
        'id': cart.id,
        'user_id': cart.user_id,
        'total_items': cart.get_total_items(),
        'total_price': float(cart.get_total_price()),
        'items': [
            {
                'id': item.id,
                'product_id': item.product_id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'nameAr': item.product.nameAr,
                    'sku': item.product.sku,
                    'price': float(item.product.price),
                    'stock_quantity': item.product.stock_quantity,
                    'is_in_stock': item.product.is_in_stock(),
                    'main_image': item.product.get_main_image()
                },
                'quantity': item.quantity,
                'unit_price': float(item.product.price),
                'total_price': float(item.get_total_price()),
                'added_at': item.added_at.isoformat()
            }
            for item in cart.items
        ],
        'created_at': cart.created_at.isoformat(),
        'updated_at': cart.updated_at.isoformat()
    }
    
    return jsonify({
        'message': 'Cart retrieved successfully',
        'data': cart_data
    }), 200

@bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or not data.get('product_id'):
        return jsonify({'error': 'Product ID is required'}), 400
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    # Check if product exists and is active
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check stock availability
    if product.stock_quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    # Get or create cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()  # Get cart ID
    
    # Check if item already exists in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        # Update quantity
        new_quantity = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            return jsonify({'error': 'Insufficient stock for total quantity'}), 400
        cart_item.quantity = new_quantity
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    cart.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Item added to cart successfully',
            'data': {
                'cart_id': cart.id,
                'item_id': cart_item.id,
                'product_id': product_id,
                'quantity': cart_item.quantity,
                'total_items': cart.get_total_items(),
                'total_price': float(cart.get_total_price())
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add item to cart', 'details': str(e)}), 500

@bp.route('/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return jsonify({'error': 'Quantity is required'}), 400
    
    quantity = data['quantity']
    
    if quantity < 0:
        return jsonify({'error': 'Quantity cannot be negative'}), 400
    
    # Get cart item
    cart_item = CartItem.query.join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == user_id
    ).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    if quantity == 0:
        # Remove item
        db.session.delete(cart_item)
    else:
        # Check stock availability
        if cart_item.product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
    
    cart_item.cart.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        # Get updated cart totals
        cart = cart_item.cart if quantity > 0 else Cart.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'message': 'Cart item updated successfully',
            'data': {
                'total_items': cart.get_total_items() if cart else 0,
                'total_price': float(cart.get_total_price()) if cart else 0
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update cart item', 'details': str(e)}), 500

@bp.route('/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(item_id):
    """Remove item from cart"""
    user_id = int(get_jwt_identity())
    
    # Get cart item
    cart_item = CartItem.query.join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == user_id
    ).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    cart = cart_item.cart
    db.session.delete(cart_item)
    cart.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Item removed from cart successfully',
            'data': {
                'total_items': cart.get_total_items(),
                'total_price': float(cart.get_total_price())
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove item from cart', 'details': str(e)}), 500

@bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear all items from cart"""
    user_id = int(get_jwt_identity())
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Cart is already empty'}), 200
    
    cart.clear()
    cart.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Cart cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to clear cart', 'details': str(e)}), 500

@bp.route('/count', methods=['GET'])
@jwt_required()
def get_cart_count():
    """Get cart item count"""
    user_id = int(get_jwt_identity())
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        'message': 'Cart count retrieved successfully',
        'data': {
            'total_items': cart.get_total_items() if cart else 0,
            'unique_items': len(cart.items) if cart else 0
        }
    }), 200

@bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_cart():
    """Validate cart items (stock availability, price changes)"""
    user_id = int(get_jwt_identity())
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    issues = []
    
    for item in cart.items:
        product = item.product
        
        # Check if product is still active
        if not product.is_active:
            issues.append({
                'item_id': item.id,
                'product_id': product.id,
                'product_name': product.name,
                'issue': 'Product is no longer available',
                'action': 'remove'
            })
            continue
        
        # Check stock availability
        if product.stock_quantity < item.quantity:
            issues.append({
                'item_id': item.id,
                'product_id': product.id,
                'product_name': product.name,
                'issue': f'Only {product.stock_quantity} items available',
                'action': 'reduce_quantity',
                'available_quantity': product.stock_quantity
            })
    
    return jsonify({
        'message': 'Cart validation completed',
        'data': {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_items': cart.get_total_items(),
            'total_price': float(cart.get_total_price())
        }
    }), 200
