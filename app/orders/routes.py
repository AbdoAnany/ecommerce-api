from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from decimal import Decimal
from app.orders import bp
from app.models import (
    Order, OrderItem, Cart, Address, Product, Payment,
    OrderStatus, PaymentStatus, User
)
from app import db

@bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create order from cart"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Validate required data
    if not data or not data.get('shipping_address_id'):
        return jsonify({'error': 'Shipping address is required'}), 400
    
    # Get shipping address
    shipping_address = Address.query.filter_by(
        id=data['shipping_address_id'],
        user_id=user_id
    ).first()
    
    if not shipping_address:
        return jsonify({'error': 'Shipping address not found'}), 404
    
    # Get billing address (use shipping if not provided)
    billing_address_id = data.get('billing_address_id', data['shipping_address_id'])
    billing_address = Address.query.filter_by(
        id=billing_address_id,
        user_id=user_id
    ).first()
    
    if not billing_address:
        return jsonify({'error': 'Billing address not found'}), 404
    
    # Validate cart items
    for item in cart.items:
        if not item.product.is_active:
            return jsonify({'error': f'Product {item.product.name} is no longer available'}), 400
        
        if item.product.stock_quantity < item.quantity:
            return jsonify({'error': f'Insufficient stock for {item.product.name}'}), 400
    
    # Calculate totals
    subtotal = cart.get_total_price()
    tax_rate = Decimal('0.10')  # 10% tax - make this configurable
    tax_amount = subtotal * tax_rate
    shipping_amount = Decimal('10.00')  # Fixed shipping - make this configurable
    discount_amount = Decimal('0.00')  # TODO: Apply coupons
    total_amount = subtotal + tax_amount + shipping_amount - discount_amount
    
    # Create order
    order = Order(
        user_id=user_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        currency=current_app.config.get('DEFAULT_CURRENCY', 'USD'),
        shipping_address={
            'first_name': shipping_address.first_name,
            'last_name': shipping_address.last_name,
            'company': shipping_address.company,
            'address_line_1': shipping_address.address_line_1,
            'address_line_2': shipping_address.address_line_2,
            'city': shipping_address.city,
            'state': shipping_address.state,
            'postal_code': shipping_address.postal_code,
            'country': shipping_address.country,
            'phone': shipping_address.phone
        },
        billing_address={
            'first_name': billing_address.first_name,
            'last_name': billing_address.last_name,
            'company': billing_address.company,
            'address_line_1': billing_address.address_line_1,
            'address_line_2': billing_address.address_line_2,
            'city': billing_address.city,
            'state': billing_address.state,
            'postal_code': billing_address.postal_code,
            'country': billing_address.country,
            'phone': billing_address.phone
        },
        notes=data.get('notes')
    )
    
    try:
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.product.price * cart_item.quantity,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku
            )
            db.session.add(order_item)
            
            # Update product stock
            cart_item.product.stock_quantity -= cart_item.quantity
        
        # Create payment record
        payment_method = data.get('payment_method', 'pending')
        payment = Payment(
            order_id=order.id,
            payment_method=payment_method,
            amount=total_amount,
            currency=order.currency,
            status=PaymentStatus.PENDING
        )
        db.session.add(payment)
        
        # Clear cart
        cart.clear()
        
        db.session.commit()
        
        # Return order details
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
            'payment': {
                'id': payment.id,
                'method': payment.payment_method,
                'status': payment.status.value,
                'amount': float(payment.amount)
            },
            'created_at': order.created_at.isoformat()
        }
        
        return jsonify({
            'message': 'Order created successfully',
            'data': order_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create order', 'details': str(e)}), 500

@bp.route('/<int:order_id>/payment', methods=['POST'])
@jwt_required()
def process_payment(order_id):
    """Process payment for order"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get order
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status != OrderStatus.PENDING:
        return jsonify({'error': 'Order cannot be paid'}), 400
    
    payment_method = data.get('payment_method')
    if not payment_method:
        return jsonify({'error': 'Payment method is required'}), 400
    
    # TODO: Integrate with actual payment gateway (Stripe, PayPal, etc.)
    # For now, simulate payment processing
    
    try:
        # Update payment
        payment = order.payment
        payment.payment_method = payment_method
        payment.status = PaymentStatus.COMPLETED
        payment.gateway_response = {
            'transaction_id': f'sim_{order.order_number}_{datetime.now().timestamp()}',
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'method': payment_method
        }
        
        # Update order status
        order.status = OrderStatus.PAID
        order.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment processed successfully',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'status': order.status.value,
                'payment_status': payment.status.value,
                'total_amount': float(order.total_amount)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Payment processing failed', 'details': str(e)}), 500

@bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel order"""
    user_id = int(get_jwt_identity())
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
        return jsonify({'error': 'Order cannot be cancelled'}), 400
    
    try:
        # Restore product stock
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_quantity += item.quantity
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        
        # Update payment status if exists
        if order.payment and order.payment.status == PaymentStatus.COMPLETED:
            order.payment.status = PaymentStatus.REFUNDED
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'status': order.status.value
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel order', 'details': str(e)}), 500

@bp.route('/<order_number>', methods=['GET'])
@jwt_required()
def get_order_by_number(order_number):
    """Get order by order number"""
    user_id = int(get_jwt_identity())
    
    order = Order.query.filter_by(order_number=order_number, user_id=user_id).first()
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
        } if order.payment else None,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
    }
    
    return jsonify({
        'message': 'Order retrieved successfully',
        'data': order_data
    }), 200

@bp.route('/guest', methods=['POST'])
def create_guest_order():
    """Create order for guest user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Order data is required'}), 400
    
    # Validate required fields
    required_fields = ['items', 'shipping_address', 'contact_email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    items_data = data['items']
    if not items_data:
        return jsonify({'error': 'Order items are required'}), 400
    
    # Validate items and calculate totals
    subtotal = Decimal('0.00')
    order_items = []
    
    for item_data in items_data:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        if not product_id or quantity <= 0:
            return jsonify({'error': 'Invalid item data'}), 400
        
        product = Product.query.filter_by(id=product_id, is_active=True).first()
        if not product:
            return jsonify({'error': f'Product {product_id} not found'}), 404
        
        if product.stock_quantity < quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
        
        item_total = product.price * quantity
        subtotal += item_total
        
        order_items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': product.price,
            'total_price': item_total
        })
    
    # Calculate totals
    tax_rate = Decimal('0.10')
    tax_amount = subtotal * tax_rate
    shipping_amount = Decimal('10.00')
    total_amount = subtotal + tax_amount + shipping_amount
    
    # Create guest order
    order = Order(
        user_id=None,  # Guest order
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total_amount=total_amount,
        shipping_address=data['shipping_address'],
        billing_address=data.get('billing_address', data['shipping_address']),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                product_name=item_data['product'].name,
                product_sku=item_data['product'].sku
            )
            db.session.add(order_item)
            
            # Update stock
            item_data['product'].stock_quantity -= item_data['quantity']
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            payment_method='pending',
            amount=total_amount,
            status=PaymentStatus.PENDING
        )
        db.session.add(payment)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Guest order created successfully',
            'data': {
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'status': order.status.value
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create guest order', 'details': str(e)}), 500
