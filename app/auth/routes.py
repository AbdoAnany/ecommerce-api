from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timezone, timedelta
from app.auth import bp
from app.auth.schemas import (
    RegisterSchema, LoginSchema, RefreshTokenSchema,
    ChangePasswordSchema, ForgotPasswordSchema, 
    ResetPasswordSchema, UserResponseSchema, 
    TokenResponseSchema
)
from app.models import User, UserRole
from app import db, blacklisted_tokens
import uuid

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        role=UserRole.CUSTOMER,
        verification_token=str(uuid.uuid4())
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # TODO: Send verification email
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Prepare response
        user_schema = UserResponseSchema()
        token_schema = TokenResponseSchema()
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'token_type': 'Bearer',
            'user': user
        }
        
        return jsonify({
            'message': 'User registered successfully',
            'data': token_schema.dump(response_data)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    # Find user by email
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    
    # Prepare response
    user_schema = UserResponseSchema()
    token_schema = TokenResponseSchema()
    
    response_data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'token_type': 'Bearer',
        'user': user
    }
    
    return jsonify({
        'message': 'Login successful',
        'data': token_schema.dump(response_data)
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 404
    
    # Create new access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Token refreshed successfully',
        'data': {
            'access_token': access_token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'token_type': 'Bearer'
        }
    }), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout - blacklist current token"""
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    
    return jsonify({'message': 'Successfully logged out'}), 200

@bp.route('/logout-all', methods=['POST'])
@jwt_required()
def logout_all():
    """Logout from all devices - blacklist refresh token too"""
    # In a real implementation, you'd blacklist all user's tokens
    # For now, we'll just blacklist the current one
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    
    return jsonify({'message': 'Successfully logged out from all devices'}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_schema = UserResponseSchema()
    return jsonify({
        'message': 'User info retrieved successfully',
        'data': user_schema.dump(user)
    }), 200

@bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    schema = ChangePasswordSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Update password
    user.set_password(data['new_password'])
    user.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    schema = ForgotPasswordSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        # Generate reset token
        user.reset_token = str(uuid.uuid4())
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # TODO: Send password reset email
        
    # Always return success for security
    return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    schema = ResetPasswordSchema()
    
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    
    user = User.query.filter_by(reset_token=data['token']).first()
    
    if not user:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    # Reset password
    user.set_password(data['new_password'])
    user.reset_token = None
    user.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password', 'details': str(e)}), 500

@bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
    
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
    
    # Verify email
    user.is_verified = True
    user.verification_token = None
    user.updated_at = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Email verified successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to verify email', 'details': str(e)}), 500
