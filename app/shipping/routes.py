from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from app.shipping import bp
from app.models import Address, User
from app import db

@bp.route('/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    """Get user's addresses"""
    user_id = int(get_jwt_identity())
    
    addresses = Address.query.filter_by(user_id=user_id).order_by(
        Address.is_default.desc(), Address.created_at.desc()
    ).all()
    
    address_list = [
        {
            'id': address.id,
            'type': address.type,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'full_name': address.get_full_name(),
            'company': address.company,
            'address_line_1': address.address_line_1,
            'address_line_2': address.address_line_2,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country,
            'phone': address.phone,
            'is_default': address.is_default,
            'full_address': address.get_full_address(),
            'created_at': address.created_at.isoformat(),
            'updated_at': address.updated_at.isoformat()
        }
        for address in addresses
    ]
    
    return jsonify({
        'message': 'Addresses retrieved successfully',
        'data': address_list
    }), 200

@bp.route('/addresses', methods=['POST'])
@jwt_required()
def create_address():
    """Create new address"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Address data is required'}), 400
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'address_line_1', 'city', 'state', 'postal_code', 'country']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if this should be the default address
    is_default = data.get('is_default', False)
    
    # If setting as default, remove default from other addresses
    if is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # If no addresses exist, make this the default
    if not Address.query.filter_by(user_id=user_id).first():
        is_default = True
    
    address = Address(
        user_id=user_id,
        type=data.get('type', 'shipping'),
        first_name=data['first_name'],
        last_name=data['last_name'],
        company=data.get('company'),
        address_line_1=data['address_line_1'],
        address_line_2=data.get('address_line_2'),
        city=data['city'],
        state=data['state'],
        postal_code=data['postal_code'],
        country=data['country'],
        phone=data.get('phone'),
        is_default=is_default
    )
    
    try:
        db.session.add(address)
        db.session.commit()
        
        return jsonify({
            'message': 'Address created successfully',
            'data': {
                'id': address.id,
                'type': address.type,
                'full_name': address.get_full_name(),
                'full_address': address.get_full_address(),
                'is_default': address.is_default
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create address', 'details': str(e)}), 500

@bp.route('/addresses/<int:address_id>', methods=['GET'])
@jwt_required()
def get_address(address_id):
    """Get specific address"""
    user_id = int(get_jwt_identity())
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    address_data = {
        'id': address.id,
        'type': address.type,
        'first_name': address.first_name,
        'last_name': address.last_name,
        'company': address.company,
        'address_line_1': address.address_line_1,
        'address_line_2': address.address_line_2,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        'country': address.country,
        'phone': address.phone,
        'is_default': address.is_default,
        'created_at': address.created_at.isoformat(),
        'updated_at': address.updated_at.isoformat()
    }
    
    return jsonify({
        'message': 'Address retrieved successfully',
        'data': address_data
    }), 200

@bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    """Update address"""
    user_id = int(get_jwt_identity())
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    updatable_fields = [
        'type', 'first_name', 'last_name', 'company', 'address_line_1', 
        'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(address, field, data[field])
    
    # Handle default address setting
    if 'is_default' in data and data['is_default']:
        # Remove default from other addresses
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        address.is_default = True
    
    address.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Address updated successfully',
            'data': {
                'id': address.id,
                'full_name': address.get_full_name(),
                'full_address': address.get_full_address(),
                'is_default': address.is_default
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update address', 'details': str(e)}), 500

@bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    """Delete address"""
    user_id = int(get_jwt_identity())
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    # If deleting default address, set another address as default
    if address.is_default:
        other_address = Address.query.filter(
            Address.user_id == user_id,
            Address.id != address_id
        ).first()
        
        if other_address:
            other_address.is_default = True
    
    try:
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({'message': 'Address deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete address', 'details': str(e)}), 500

@bp.route('/addresses/<int:address_id>/set-default', methods=['POST'])
@jwt_required()
def set_default_address(address_id):
    """Set address as default"""
    user_id = int(get_jwt_identity())
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    # Remove default from other addresses
    Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # Set this address as default
    address.is_default = True
    address.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Default address updated successfully',
            'data': {
                'id': address.id,
                'full_name': address.get_full_name(),
                'full_address': address.get_full_address(),
                'is_default': address.is_default
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to set default address', 'details': str(e)}), 500

@bp.route('/addresses/default', methods=['GET'])
@jwt_required()
def get_default_address():
    """Get user's default address"""
    user_id = int(get_jwt_identity())
    
    address = Address.query.filter_by(user_id=user_id, is_default=True).first()
    
    if not address:
        # Get any address if no default is set
        address = Address.query.filter_by(user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'No addresses found'}), 404
    
    address_data = {
        'id': address.id,
        'type': address.type,
        'first_name': address.first_name,
        'last_name': address.last_name,
        'full_name': address.get_full_name(),
        'company': address.company,
        'address_line_1': address.address_line_1,
        'address_line_2': address.address_line_2,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        'country': address.country,
        'phone': address.phone,
        'is_default': address.is_default,
        'full_address': address.get_full_address()
    }
    
    return jsonify({
        'message': 'Default address retrieved successfully',
        'data': address_data
    }), 200

@bp.route('/calculate-shipping', methods=['POST'])
@jwt_required()
def calculate_shipping():
    """Calculate shipping cost"""
    data = request.get_json()
    
    if not data or not data.get('address_id'):
        return jsonify({'error': 'Address ID is required'}), 400
    
    user_id = int(get_jwt_identity())
    address = Address.query.filter_by(id=data['address_id'], user_id=user_id).first()
    
    if not address:
        return jsonify({'error': 'Address not found'}), 404
    
    # Simple shipping calculation (make this more sophisticated based on requirements)
    total_weight = data.get('total_weight', 0)
    total_value = data.get('total_value', 0)
    
    # Base shipping rates
    base_shipping = 10.00
    
    # Add weight-based charges
    if total_weight > 5:  # kg
        base_shipping += (total_weight - 5) * 2.00
    
    # Free shipping for orders over certain amount
    if total_value > 100:
        base_shipping = 0
    
    # International shipping
    if address.country.upper() != 'US':
        base_shipping += 15.00
    
    # Express shipping option
    express_shipping = base_shipping * 2 if base_shipping > 0 else 25.00
    
    shipping_options = [
        {
            'method': 'standard',
            'name': 'Standard Shipping',
            'cost': base_shipping,
            'estimated_days': '5-7',
            'description': 'Standard delivery'
        }
    ]
    
    if total_value > 50:  # Offer express only for higher value orders
        shipping_options.append({
            'method': 'express',
            'name': 'Express Shipping',
            'cost': express_shipping,
            'estimated_days': '1-2',
            'description': 'Fast delivery'
        })
    
    return jsonify({
        'message': 'Shipping calculated successfully',
        'data': {
            'address': {
                'id': address.id,
                'full_address': address.get_full_address(),
                'country': address.country
            },
            'shipping_options': shipping_options
        }
    }), 200
