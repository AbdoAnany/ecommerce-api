from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Product, Category

# Base field definitions for reuse
PRODUCT_BASE_FIELDS = {
    'name_en': fields.Str(validate=validate.Length(min=1, max=200)),
    'name_ar': fields.Str(validate=validate.Length(max=200)),
    'description_en': fields.Str(),
    'description_ar': fields.Str(),
    'short_description': fields.Str(validate=validate.Length(max=500)),
    'sku': fields.Str(validate=validate.Length(min=1, max=100)),
    'price': fields.Decimal(validate=validate.Range(min=0)),
    'discount_price': fields.Decimal(validate=validate.Range(min=0)),
    'cost_price': fields.Decimal(validate=validate.Range(min=0)),
    'stock_quantity': fields.Int(validate=validate.Range(min=0)),
    'min_stock': fields.Int(validate=validate.Range(min=0)),
    'low_stock_threshold': fields.Int(validate=validate.Range(min=0)),
    'weight': fields.Decimal(validate=validate.Range(min=0)),
    'dimensions': fields.Str(validate=validate.Length(max=100)),
    'is_active': fields.Bool(),
    'is_featured': fields.Bool(),
    'is_new': fields.Bool(),
    'is_on_sale': fields.Bool(),
    'is_organic': fields.Bool(),
    'is_digital': fields.Bool(),
    'requires_shipping': fields.Bool(),
    'meta_title': fields.Str(validate=validate.Length(max=200)),
    'meta_description': fields.Str(validate=validate.Length(max=500)),
    'slug': fields.Str(validate=validate.Length(max=200)),
    'category_id': fields.Int(),
    'tags': fields.List(fields.Str()),
    'brand': fields.Str(validate=validate.Length(max=100)),
    'currency': fields.Str(validate=validate.Length(max=3)),
    'availability': fields.Str(validate=validate.Length(max=20)),
    'unit_measure_en': fields.Str(validate=validate.Length(max=50)),
    'unit_measure_ar': fields.Str(validate=validate.Length(max=50)),
    'unit_value': fields.Decimal(validate=validate.Range(min=0)),
    'package_type': fields.Str(validate=validate.Length(max=50)),
    'country_of_origin': fields.Str(validate=validate.Length(max=100)),
    'ingredients': fields.Str(),
    'usage_instructions_en': fields.Str(),
    'usage_instructions_ar': fields.Str(),
    'warnings_en': fields.Str(),
    'warnings_ar': fields.Str(),
    'min_qty': fields.Int(validate=validate.Range(min=1)),
    'step_qty': fields.Int(validate=validate.Range(min=1)),
    'max_qty': fields.Int(validate=validate.Range(min=1)),
}

class ProductCreateSchema(Schema):
    """Schema for creating products"""
    
    # Required fields
    name_en = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    category_id = fields.Int(required=True)
    
    # Optional fields (using base definitions)
    locals().update({k: v for k, v in PRODUCT_BASE_FIELDS.items() 
                    if k not in ['name_en', 'sku', 'price', 'category_id']})
    
    @validates('sku')
    def validate_sku(self, value):
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product:
            raise ValidationError('SKU already exists.')
    
    @validates('category_id')
    def validate_category_id(self, value):
        if value is not None:
            category = Category.query.get(value)
            if not category:
                raise ValidationError('Category does not exist.')

class ProductUpdateSchema(Schema):
    """Schema for updating products"""
    
    # All fields optional for updates
    locals().update(PRODUCT_BASE_FIELDS)
    
    @validates('sku')
    def validate_sku(self, value):
        product_id = self.context.get('product_id')
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product and existing_product.id != product_id:
            raise ValidationError('SKU already exists.')

class ProductImageSchema(Schema):
    """Schema for product images"""
    id = fields.Int()
    url = fields.Str()
    alt_text = fields.Str()
    is_primary = fields.Bool()
    sort_order = fields.Int()

class ProductTagSchema(Schema):
    """Schema for product tags"""
    id = fields.Int()
    name = fields.Str()

class ProductMixin:
    """Mixin for common product methods"""
    
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
    
    def get_category_detail(self, obj):
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

class ProductListSchema(Schema, ProductMixin):
    """Schema for product listings"""
    id = fields.Int()
    name_en = fields.Str()
    name_ar = fields.Str()
    short_description = fields.Str()
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

class ProductDetailSchema(Schema, ProductMixin):
    """Schema for detailed product view"""
    id = fields.Int()
    name_en = fields.Str()
    name_ar = fields.Str()
    description_en = fields.Str()
    description_ar = fields.Str()
    short_description = fields.Str()
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
    meta_title = fields.Str()
    meta_description = fields.Str()
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
    category = fields.Method('get_category_detail')
    tags = fields.Nested(ProductTagSchema, many=True)
    average_rating = fields.Method('get_average_rating')
    review_count = fields.Method('get_review_count')
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
