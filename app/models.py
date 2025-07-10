from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid

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
    name_en = db.Column(db.String(100), nullable=False)  # English name (primary)
    name_ar = db.Column(db.String(100))  # Arabic name
    description_en = db.Column(db.Text)  # English description
    description_ar = db.Column(db.Text)  # Arabic description
    
    # Multi-language slugs
    slug_en = db.Column(db.String(100), nullable=False, index=True)  # English slug
    slug_ar = db.Column(db.String(100), index=True)  # Arabic slug
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)  # Primary slug (for compatibility)
    
    # Media and display
    thumbnail = db.Column(db.String(500))  # Category thumbnail image URL
    image_url = db.Column(db.String(255))  # Keep for backward compatibility
    
    # Category features
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, default=0)  # Display position/order
    sort_order = db.Column(db.Integer, default=0)  # Keep for backward compatibility
    
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Metadata
    type = db.Column(db.String(50), default='category')  # category, subcategory, etc.
    status = db.Column(db.String(20), default='active')  # active, inactive, draft
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Self-referential relationship for hierarchical categories
    parent = db.relationship('Category', remote_side=[id], backref='children')
    products = db.relationship('Product', backref='category', lazy=True)
    
    def get_name(self, lang='en'):
        """Get category name in specified language"""
        return self.name_ar if lang == 'ar' and self.name_ar else self.name_en
    
    def get_description(self, lang='en'):
        """Get category description in specified language"""
        return self.description_ar if lang == 'ar' and self.description_ar else self.description_en
    
    def get_slug(self, lang='en'):
        """Get category slug in specified language"""
        return self.slug_ar if lang == 'ar' and self.slug_ar else self.slug_en
    
    def get_product_count(self):
        """Get total number of products in this category and subcategories"""
        count = len(self.products)
        for child in self.children:
            count += child.get_product_count()
        return count
    
    def get_stock_total(self):
        """Get total stock for all products in this category and subcategories"""
        total = sum(product.stock_quantity for product in self.products if product.is_active)
        for child in self.children:
            total += child.get_stock_total()
        return total
    
    def get_children_count(self):
        """Get number of direct children categories"""
        return len([child for child in self.children if child.is_active])
    
    def get_breadcrumbs(self, lang='en'):
        """Get breadcrumb trail for this category"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'id': str(current.id),
                'name': {
                    'en': current.name_en,
                    'ar': current.name_ar or current.name_en
                }
            })
            current = current.parent
        return breadcrumbs
    
    def to_dict(self, lang='en', include_meta=True, include_breadcrumbs=True):
        """Convert category to dictionary format matching the JSON structure"""
        data = {
            'id': str(self.id),
            'name': {
                'en': self.name_en,
                'ar': self.name_ar or self.name_en
            },
            'slug': {
                'en': self.slug_en or self.slug,
                'ar': self.slug_ar or self.slug_en or self.slug
            },
            'thumbnail': self.thumbnail or self.image_url,
            'parent': None,
            'children_count': self.get_children_count(),
            'is_featured': self.is_featured,
            'position': self.position,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Add parent information if exists
        if self.parent:
            data['parent'] = {
                'id': str(self.parent.id),
                'name': {
                    'en': self.parent.name_en,
                    'ar': self.parent.name_ar or self.parent.name_en
                }
            }
        
        # Add breadcrumbs
        if include_breadcrumbs:
            data['breadcrumbs'] = self.get_breadcrumbs(lang)
        
        # Add meta information
        if include_meta:
            data['meta'] = {
                'product_count': self.get_product_count(),
                'stock_total': self.get_stock_total()
            }
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name_en}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Tag {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-language name and description (stored as JSON)
    name_en = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Product identification and images
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    thumbnail = db.Column(db.String(500))  # Main product image URL
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    
    # Pricing (support for multiple currencies and discounts)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_price = db.Column(db.Numeric(10, 2), default=0)  # Discount amount
    currency = db.Column(db.String(3), default='USD')  # Currency code (USD, EGP, etc.)
    cost_price = db.Column(db.Numeric(10, 2))  # Internal cost
    
    # Inventory management
    stock_quantity = db.Column(db.Integer, default=0, nullable=False, name='stock')
    min_stock = db.Column(db.Integer, default=0)  # Minimum stock level
    low_stock_threshold = db.Column(db.Integer, default=10)
    availability = db.Column(db.String(20), default='in_stock')  # in_stock, out_of_stock, pre_order
    
    # Product attributes
    brand = db.Column(db.String(100))
    unit_measure_en = db.Column(db.String(50))  # milliliter, gram, piece, etc.
    unit_measure_ar = db.Column(db.String(50))
    unit_value = db.Column(db.Numeric(10, 2))  # 500 (for 500ml)
    package_type = db.Column(db.String(50))  # Bottle, Box, Tube, etc.
    country_of_origin = db.Column(db.String(100))
    expiration_date = db.Column(db.Date)
    
    # Product specifications
    weight = db.Column(db.Numeric(8, 2))
    dimensions = db.Column(db.String(100))  # e.g., "10x5x3 cm"
    ingredients = db.Column(db.Text)  # JSON array as text
    
    # Usage and safety information
    usage_instructions_en = db.Column(db.Text)
    usage_instructions_ar = db.Column(db.Text)
    warnings_en = db.Column(db.Text)
    warnings_ar = db.Column(db.Text)
    
    # Ordering constraints
    min_qty = db.Column(db.Integer, default=1)  # Minimum order quantity
    step_qty = db.Column(db.Integer, default=1)  # Quantity step (e.g., sold in pairs)
    max_qty = db.Column(db.Integer, default=100)  # Maximum order quantity
    
    # Product flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_new = db.Column(db.Boolean, default=False, nullable=False)
    is_on_sale = db.Column(db.Boolean, default=False, nullable=False)
    is_organic = db.Column(db.Boolean, default=False, nullable=False)
    is_digital = db.Column(db.Boolean, default=False, nullable=False)
    requires_shipping = db.Column(db.Boolean, default=True, nullable=False)
    
    # SEO fields
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    
    # Relationships
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=product_tags, backref=db.backref('products', lazy=True))
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    
    # Utility methods
    def get_name(self, lang='en'):
        """Get product name in specified language"""
        return self.name_ar if lang == 'ar' and self.name_ar else self.name_en
    
    def get_description(self, lang='en'):
        """Get product description in specified language"""
        return self.description_ar if lang == 'ar' and self.description_ar else self.description_en
    
    def get_unit_measure(self, lang='en'):
        """Get unit measure in specified language"""
        return self.unit_measure_ar if lang == 'ar' and self.unit_measure_ar else self.unit_measure_en
    
    def get_usage_instructions(self, lang='en'):
        """Get usage instructions in specified language"""
        return self.usage_instructions_ar if lang == 'ar' and self.usage_instructions_ar else self.usage_instructions_en
    
    def get_warnings(self, lang='en'):
        """Get warnings in specified language"""
        return self.warnings_ar if lang == 'ar' and self.warnings_ar else self.warnings_en
    
    def get_final_price(self):
        """Calculate final price after discount"""
        if self.discount_price and self.discount_price > 0:
            return max(0, float(self.price) - float(self.discount_price))
        return float(self.price)
    
    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.discount_price > 0 and self.price > 0:
            return round((float(self.discount_price) / float(self.price)) * 100, 2)
        return 0
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0 and self.availability == 'in_stock'
    
    def is_low_stock(self):
        """Check if product is low in stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    def get_stock_status(self):
        """Get stock status"""
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            return 'low_stock'
        elif self.stock_quantity <= self.min_stock:
            return 'critical_stock'
        return 'in_stock'
    
    def get_average_rating(self):
        """Get average rating from reviews"""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    def get_review_count(self):
        """Get total number of reviews"""
        return len(self.reviews)
    
    def get_main_image(self):
        """Get main product image"""
        if self.thumbnail:
            return self.thumbnail
        main_image = next((img for img in self.images if img.is_primary), None)
        return main_image.url if main_image else None
    
    def get_ingredients_list(self):
        """Get ingredients as a list"""
        if self.ingredients:
            try:
                import json
                return json.loads(self.ingredients)
            except:
                return self.ingredients.split(',') if ',' in self.ingredients else [self.ingredients]
        return []
    
    def set_ingredients_list(self, ingredients_list):
        """Set ingredients from a list"""
        if isinstance(ingredients_list, list):
            import json
            self.ingredients = json.dumps(ingredients_list)
        else:
            self.ingredients = str(ingredients_list)
    
    def to_dict(self, lang='en', include_relations=False):
        """Convert product to dictionary format matching the JSON structure"""
        data = {
            'id': str(self.id),
            'name': {
                'en': self.name_en,
                'ar': self.name_ar or self.name_en
            },
            'description': {
                'en': self.description_en,
                'ar': self.description_ar or self.description_en
            },
            'thumbnail': self.thumbnail or self.get_main_image(),
            'sku': self.sku,
            'price': float(self.price),
            'discountPrice': float(self.discount_price or 0),
            'finalPrice': self.get_final_price(),
            'currency': self.currency,
            'stock': self.stock_quantity,
            'inStock': self.is_in_stock(),
            'minStock': self.min_stock,
            'availability': self.availability,
            'tags': [tag.name for tag in self.tags] if include_relations else [],
            'featured': self.is_featured,
            'isNew': self.is_new,
            'onSale': self.is_on_sale,
            'unitMeasure': {
                'en': self.unit_measure_en,
                'ar': self.unit_measure_ar or self.unit_measure_en
            },
            'unitValue': float(self.unit_value) if self.unit_value else None,
            'ordering': {
                'minQty': self.min_qty,
                'stepQty': self.step_qty,
                'maxQty': self.max_qty
            },
            'brand': self.brand,
            'expirationDate': self.expiration_date.isoformat() if self.expiration_date else None,
            'countryOfOrigin': self.country_of_origin,
            'ingredients': self.get_ingredients_list(),
            'isOrganic': self.is_organic,
            'packageType': self.package_type,
            'usageInstructions': {
                'en': self.usage_instructions_en,
                'ar': self.usage_instructions_ar or self.usage_instructions_en
            },
            'warnings': {
                'en': self.warnings_en,
                'ar': self.warnings_ar or self.warnings_en
            },
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'status': 'active' if self.is_active else 'inactive'
        }
        
        if include_relations and self.category:
            data['category'] = {
                'id': str(self.category.id),
                'name': {
                    'en': self.category.name_en,
                    'ar': self.category.name_ar or self.category.name_en
                }
            }
        
        return data
    
    def __repr__(self):
        return f'<Product {self.name_en}>'

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
        return f'<CartItem {self.product.name_en} x{self.quantity}>'

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
