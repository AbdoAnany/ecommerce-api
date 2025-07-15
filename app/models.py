from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid
from sqlalchemy import JSON

class UserRole(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    VENDOR = "vendor"

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Association table for product tags
product_tags = db.Table('product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255))
    reset_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    cart = db.relationship('Cart', backref='user', uselist=False, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(JSON, nullable=False)  # {"en": "...", "ar": "..."}
    description = db.Column(JSON)  # {"en": "...", "ar": "..."}
    slug = db.Column(db.String(150), unique=True, nullable=False)
    image_url = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    # Relationships
    parent = db.relationship('Category', remote_side=[id], backref='children')
    # Remove duplicate products relationship since it's defined in Product model
    # brands = db.relationship('Brand', secondary=category_brands, backref='categories')  # Uncomment if you have a Brand model

    @property
    def products_count(self):
        return len(self.products)

    def get_name(self, lang='en'):
        """Get the category name in the specified language"""
        if isinstance(self.name, dict):
            return self.name.get(lang, self.name.get('en', ''))
        return self.name or ''

    def get_description(self, lang='en'):
        """Get the category description in the specified language"""
        if isinstance(self.description, dict):
            return self.description.get(lang, self.description.get('en', ''))
        return self.description or ''

    def set_name(self, name_en, name_ar=None):
        """Set the category name in English and optionally Arabic"""
        self.name = {
            'en': name_en,
            'ar': name_ar or name_en
        }

    def set_description(self, desc_en, desc_ar=None):
        """Set the category description in English and optionally Arabic"""
        self.description = {
            'en': desc_en,
            'ar': desc_ar or desc_en
        }

    def __repr__(self):
        return f'<Category {self.get_name("en")}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Tag {self.name}>'



class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(JSON, nullable=False)  # {"en": "...", "ar": "..."}
    description = db.Column(JSON)
    thumbnail = db.Column(db.String(255))
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2), default=0)
    stock = db.Column(db.Integer, default=0, nullable=False)
    in_stock = db.Column(db.Boolean, default=True, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    unitMeasure = db.Column(JSON)
    unitValue = db.Column(db.Integer, default=1)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    low_stock_threshold = db.Column(db.Integer, default=10)  # Optional, for is_low_stock
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    # Relationships
    category = db.relationship('Category', backref='products', lazy=True)
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=product_tags, backref=db.backref('products', lazy=True))
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

    def get_name(self, lang='en'):
        """Get the product name in the specified language"""
        if isinstance(self.name, dict):
            return self.name.get(lang, self.name.get('en', ''))
        return self.name or ''

    def get_description(self, lang='en'):
        """Get the product description in the specified language"""
        if isinstance(self.description, dict):
            return self.description.get(lang, self.description.get('en', ''))
        return self.description or ''

    def get_unit_measure(self, lang='en'):
        """Get the unit measure in the specified language"""
        if isinstance(self.unitMeasure, dict):
            return self.unitMeasure.get(lang, self.unitMeasure.get('en', ''))
        return self.unitMeasure or ''

    def set_name(self, name_en, name_ar=None):
        """Set the product name in English and optionally Arabic"""
        self.name = {
            'en': name_en,
            'ar': name_ar or name_en
        }

    def set_description(self, desc_en, desc_ar=None):
        """Set the product description in English and optionally Arabic"""
        self.description = {
            'en': desc_en,
            'ar': desc_ar or desc_en
        }

    def set_unit_measure(self, unit_en, unit_ar=None):
        """Set the unit measure in English and optionally Arabic"""
        self.unitMeasure = {
            'en': unit_en,
            'ar': unit_ar or unit_en
        }

    def get_average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    def get_review_count(self):
        return len(self.reviews)

    def is_in_stock(self):
        return self.stock > 0

    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def get_main_image(self):
        main_image = next((img for img in self.images if img.is_primary), None)
        return main_image.url if main_image else self.thumbnail

    def __repr__(self):
        return f'<Product {self.name.get("en") if isinstance(self.name, dict) else self.name}>'


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(200))
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ProductImage {self.url}>'
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items)
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items)
    
    def clear(self):
        for item in self.items:
            db.session.delete(item)
    
    def __repr__(self):
        return f'<Cart {self.user.username}>'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_total_price(self):
        return self.product.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), default='shipping')  # shipping, billing
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100))
    address_line_1 = db.Column(db.String(255), nullable=False)
    address_line_2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.extend([self.city, self.state, self.postal_code, self.country])
        return ', '.join(parts)
    
    def __repr__(self):
        return f'<Address {self.get_full_name()}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Address snapshots
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    
    # Tracking
    tracking_number = db.Column(db.String(100))
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Metadata
    notes = db.Column(db.Text)
    currency = db.Column(db.String(3), default='USD')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Price snapshot at time of order
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Product snapshot
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, paypal, cash_on_delivery
    payment_id = db.Column(db.String(255))  # External payment ID
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    transaction_fee = db.Column(db.Numeric(10, 2), default=0)
    
    # Metadata
    gateway_response = db.Column(db.JSON)  # Store payment gateway response
    failure_reason = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Payment {self.payment_method} - {self.status.value}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Unique constraint to prevent multiple reviews per user per product
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='_user_product_review'),)
    
    def __repr__(self):
        return f'<Review {self.rating} stars by {self.user.username}>'

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    type = db.Column(db.String(20), nullable=False)  # percentage, fixed
    value = db.Column(db.Numeric(10, 2), nullable=False)
    minimum_amount = db.Column(db.Numeric(10, 2), default=0)
    maximum_discount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def is_valid(self, order_amount=0):
        if not self.is_active:
            return False, "Coupon is not active"
        
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False, "Coupon has expired"
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        if order_amount < self.minimum_amount:
            return False, f"Minimum order amount is {self.minimum_amount}"
        
        return True, "Coupon is valid"
    
    def calculate_discount(self, amount):
        if self.type == 'percentage':
            discount = amount * (self.value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # fixed
            discount = min(self.value, amount)
        
        return discount
    
    def __repr__(self):
        return f'<Coupon {self.code}>'

# Activity Log for audit trail
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # product, order, user, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id}>'
    resource_type = db.Column(db.String(50))  # product, order, user, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id}>'
