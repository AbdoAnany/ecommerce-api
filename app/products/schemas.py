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
    thumbnail = fields.Str()
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    discount_price = fields.Decimal(validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    in_stock = fields.Bool()
    featured = fields.Bool()
    unitMeasure = MultilingualField()
    unitValue = fields.Int()
    createdAt = fields.DateTime()
    tags = fields.List(fields.Str())
    category_id = fields.Int()

    @validates('sku')
    def validate_sku(self, value):
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product:
            raise ValidationError('SKU already exists.')

# ✅ Product Update Schema
class ProductUpdateSchema(Schema):
    name = MultilingualField()
    description = MultilingualField()
    thumbnail = fields.Str()
    sku = fields.Str(validate=validate.Length(min=1, max=100))
    price = fields.Decimal(validate=validate.Range(min=0))
    discount_price = fields.Decimal(validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    in_stock = fields.Bool()
    featured = fields.Bool()
    unitMeasure = MultilingualField()
    unitValue = fields.Int()
    createdAt = fields.DateTime()
    tags = fields.List(fields.Str())
    category_id = fields.Int()

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
    description = MultilingualField()
    thumbnail = fields.Str()
    sku = fields.Str()
    price = fields.Decimal()
    discount_price = fields.Decimal()
    stock = fields.Int()
    in_stock = fields.Bool()
    featured = fields.Bool()
    unitMeasure = MultilingualField()
    unitValue = fields.Int()
    createdAt = fields.DateTime()
    tags = fields.Nested(ProductTagSchema, many=True)  # Updated: nested tags
    category = fields.Method('get_category')           # Updated: method for category
    average_rating = fields.Method('get_average_rating')
    review_count = fields.Method('get_review_count')
    created_at = fields.DateTime()

    def get_category(self, obj):
        if obj.category:
            lang = self.context.get('lang', 'en')
            return {
                'id': obj.category.id,
                'name': obj.category.get_name(lang),
                'name_all': obj.category.name,
                'slug': obj.category.slug,
                'description': obj.category.get_description(lang),
                'description_all': obj.category.description
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
    thumbnail = fields.Str()
    sku = fields.Str()
    price = fields.Decimal()
    discount_price = fields.Decimal()
    stock = fields.Int()
    in_stock = fields.Bool()
    featured = fields.Bool()
    unitMeasure = MultilingualField()
    unitValue = fields.Int()
    createdAt = fields.DateTime()
    tags = fields.Nested(ProductTagSchema, many=True)  # Updated: nested tags
    category = fields.Method('get_category')           # Updated: method for category
    average_rating = fields.Method('get_average_rating')
    review_count = fields.Method('get_review_count')
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    def get_category(self, obj):
        if obj.category:
            lang = self.context.get('lang', 'en')
            return {
                'id': obj.category.id,
                'name': obj.category.get_name(lang),
                'name_all': obj.category.name,
                'slug': obj.category.slug,
                'description': obj.category.get_description(lang),
                'description_all': obj.category.description
            }
        return None

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_review_count(self, obj):
        return obj.get_review_count()
