"""
Product Schemas for E-commerce API

This module contains all Marshmallow schemas for Product operations:
- ProductCreateSchema: For creating new products
- ProductUpdateSchema: For updating existing products  
- ProductListSchema: For product listings (minimal data)
- ProductDetailSchema: For detailed product views
- ProductImageSchema: For product images
- ProductTagSchema: For product tags
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Product

# ✅ Custom field for multilingual support
class MultilingualField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict) or 'en' not in value or 'ar' not in value:
            raise ValidationError("Must be a dictionary with 'en' and 'ar' keys.")
        return value

    def _serialize(self, value, attr, obj, **kwargs):
        return value

# ✅ Product Create Schema
class ProductCreateSchema(Schema):
    name = MultilingualField(required=True)
    description = MultilingualField()
    short_description = MultilingualField()
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    category_id = fields.Int(required=True)
    
    # Multi-language fields
    # Multi-language fields
    name_ar = fields.Str(validate=validate.Length(max=200))
    description_en = fields.Str()
    description_ar = fields.Str()
    
    # Basic product info
    short_description = fields.Str(validate=validate.Length(max=500))
    
    # Pricing fields
    discount_price = fields.Decimal(validate=validate.Range(min=0))
    cost_price = fields.Decimal(validate=validate.Range(min=0))
    
    # Inventory fields
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    min_stock = fields.Int(validate=validate.Range(min=0))
    low_stock_threshold = fields.Int(validate=validate.Range(min=0))
    
    # Physical attributes
    weight = fields.Decimal(validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=100))
    
    # Feature flags
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_new = fields.Bool()
    is_on_sale = fields.Bool()
    is_organic = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = MultilingualField()
    meta_description = MultilingualField()
    slug = fields.Str(validate=validate.Length(max=200))
    
    # Classification
    tags = fields.List(fields.Str())
    image_urls = fields.List(fields.Url(), required=False)

    @validates('sku')
    def validate_sku(self, value):
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product:
            raise ValidationError('SKU already exists.')

# ✅ Product Update Schema
class ProductUpdateSchema(Schema):
    name = MultilingualField()
    description = MultilingualField()
    short_description = MultilingualField()
    sku = fields.Str(validate=validate.Length(min=1, max=100))
    price = fields.Decimal(validate=validate.Range(min=0))
    discount_price = fields.Decimal(validate=validate.Range(min=0))
    cost_price = fields.Decimal(validate=validate.Range(min=0))
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    min_stock = fields.Int(validate=validate.Range(min=0))
    low_stock_threshold = fields.Int(validate=validate.Range(min=0))
    weight = fields.Decimal(validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=100))
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_new = fields.Bool()
    is_on_sale = fields.Bool()
    is_organic = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = MultilingualField()
    meta_description = MultilingualField()
    slug = fields.Str(validate=validate.Length(max=200))
    category_id = fields.Int()
    tags = fields.List(fields.Str())
    image_urls = fields.List(fields.Url(), required=False)

    @validates('sku')
    def validate_sku(self, value):
        product_id = self.context.get('product_id')
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product and existing_product.id != product_id:
            raise ValidationError('SKU already exists.')

# ✅ Image schema
class ProductImageSchema(Schema):
    id = fields.Int()
    url = fields.Str()
    alt_text = fields.Str()
    is_primary = fields.Bool()
    sort_order = fields.Int()

# ✅ Tag schema
class ProductTagSchema(Schema):
    id = fields.Int()
    name = fields.Str()

# ✅ List schema
class ProductListSchema(Schema):
    id = fields.Int()
    name = MultilingualField()
    short_description = MultilingualField()
    sku = fields.Str()
    price = fields.Decimal()
    discount_price = fields.Decimal()
    stock_quantity = fields.Int()
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_new = fields.Bool()
    is_on_sale = fields.Bool()
    is_in_stock = fields.Method('get_is_in_stock')
    is_low_stock = fields.Method('get_is_low_stock')
    main_image = fields.Method('get_main_image')
    category = fields.Method('get_category')
    tags = fields.Nested(ProductTagSchema, many=True)
    average_rating = fields.Method('get_average_rating')
    review_count = fields.Method('get_review_count')
    created_at = fields.DateTime()

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()

    def get_main_image(self, obj):
        return obj.get_main_image()

    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name_en,
                'slug': obj.category.slug
            }
        return None

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_review_count(self, obj):
        return obj.get_review_count()

# ✅ Detail schema
class ProductDetailSchema(Schema):
    id = fields.Int()
    name = MultilingualField()
    description = MultilingualField()
    short_description = MultilingualField()
    sku = fields.Str()
    price = fields.Decimal()
    discount_price = fields.Decimal()
    cost_price = fields.Decimal()
    stock_quantity = fields.Int()
    min_stock = fields.Int()
    low_stock_threshold = fields.Int()
    weight = fields.Decimal()
    dimensions = fields.Str()
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_new = fields.Bool()
    is_on_sale = fields.Bool()
    is_organic = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = MultilingualField()
    meta_description = MultilingualField()
    slug = fields.Str()
    brand = fields.Str()
    currency = fields.Str()
    availability = fields.Str()
    unit_measure_en = fields.Str()
    unit_measure_ar = fields.Str()
    unit_value = fields.Decimal()
    package_type = fields.Str()
    country_of_origin = fields.Str()
    ingredients = fields.Str()
    usage_instructions_en = fields.Str()
    usage_instructions_ar = fields.Str()
    warnings_en = fields.Str()
    warnings_ar = fields.Str()
    min_qty = fields.Int()
    step_qty = fields.Int()
    max_qty = fields.Int()
    is_in_stock = fields.Method('get_is_in_stock')
    is_low_stock = fields.Method('get_is_low_stock')
    images = fields.Nested(ProductImageSchema, many=True)
    category = fields.Method('get_category')
    tags = fields.Nested(ProductTagSchema, many=True)
    average_rating = fields.Method('get_average_rating')
    review_count = fields.Method('get_review_count')
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()

    def get_category(self, obj):
        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name_en,
                'slug': obj.category.slug,
                'description': obj.category.description_en
            }
        return None

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_review_count(self, obj):
        return obj.get_review_count()
