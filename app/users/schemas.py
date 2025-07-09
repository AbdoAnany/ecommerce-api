from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import User

class UpdateUserSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    email = fields.Email(validate=validate.Length(max=120))
    username = fields.Str(validate=validate.Length(min=3, max=80))
    
    @validates('email')
    def validate_email(self, value):
        # Get current user ID from context (will be set in route)
        current_user_id = self.context.get('user_id')
        existing_user = User.query.filter_by(email=value).first()
        if existing_user and existing_user.id != current_user_id:
            raise ValidationError('Email already exists.')
    
    @validates('username')
    def validate_username(self, value):
        current_user_id = self.context.get('user_id')
        existing_user = User.query.filter_by(username=value).first()
        if existing_user and existing_user.id != current_user_id:
            raise ValidationError('Username already exists.')

class UserProfileSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    phone = fields.Str()
    full_name = fields.Method('get_full_name')
    role = fields.Method('get_role')
    is_active = fields.Bool()
    is_verified = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_login = fields.DateTime()
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role(self, obj):
        return obj.role.value

class UserListSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    full_name = fields.Method('get_full_name')
    role = fields.Method('get_role')
    is_active = fields.Bool()
    is_verified = fields.Bool()
    created_at = fields.DateTime()
    last_login = fields.DateTime()
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role(self, obj):
        return obj.role.value
