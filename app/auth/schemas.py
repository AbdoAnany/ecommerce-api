from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import User, UserRole

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=120))
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    
    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already exists.')
    
    @validates('username')
    def validate_username(self, value):
        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists.')

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class RefreshTokenSchema(Schema):
    refresh_token = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class UserResponseSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    phone = fields.Str()
    role = fields.Method('get_role')
    is_active = fields.Bool()
    is_verified = fields.Bool()
    created_at = fields.DateTime()
    last_login = fields.DateTime()
    
    def get_role(self, obj):
        return obj.role.value

class TokenResponseSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()
    token_type = fields.Str()
    user = fields.Nested(UserResponseSchema)
