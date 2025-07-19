from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Product
from marshmallow import Schema, fields, validate

class ProductImageSchema(Schema):
    url = fields.Str(required=True, validate=validate.Length(min=1))
    alt = fields.Str(required=False)


class ProductCreateSchema(Schema):
    id = fields.Int(required=False)  # ✅ Add this line to allow user-defined ID
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    nameAr = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    images = fields.List(fields.Nested(ProductImageSchema))

    descriptionAr = fields.Str()
    short_description = fields.Str(validate=validate.Length(max=500))
    short_descriptionAr = fields.Str(validate=validate.Length(max=500))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    compare_price = fields.Decimal(validate=validate.Range(min=0))
    cost_price = fields.Decimal(validate=validate.Range(min=0))
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    low_stock_threshold = fields.Int(validate=validate.Range(min=0))
    weight = fields.Decimal(validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=100))
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = fields.Str(validate=validate.Length(max=200))
    meta_description = fields.Str(validate=validate.Length(max=500))
    slug = fields.Str(validate=validate.Length(max=200))
    category_id = fields.Int()
    tags = fields.List(fields.Str())
    
    @validates('sku')
    def validate_sku(self, value):
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product:
            raise ValidationError('SKU already exists.')

class ProductUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=200))
    nameAr = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str()
    descriptionAr = fields.Str()
    images = fields.List(fields.Nested(ProductImageSchema))

    short_description = fields.Str(validate=validate.Length(max=500))
    short_descriptionAr = fields.Str(validate=validate.Length(max=500))
    sku = fields.Str(validate=validate.Length(min=1, max=100))
    price = fields.Decimal(validate=validate.Range(min=0))
    compare_price = fields.Decimal(validate=validate.Range(min=0))
    cost_price = fields.Decimal(validate=validate.Range(min=0))
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    low_stock_threshold = fields.Int(validate=validate.Range(min=0))
    weight = fields.Decimal(validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=100))
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = fields.Str(validate=validate.Length(max=200))
    meta_description = fields.Str(validate=validate.Length(max=500))
    slug = fields.Str(validate=validate.Length(max=200))
    category_id = fields.Int()
    tags = fields.List(fields.Str())
    
    @validates('sku')
    def validate_sku(self, value):
        product_id = self.context.get('product_id')
        existing_product = Product.query.filter_by(sku=value).first()
        if existing_product and existing_product.id != product_id:
            raise ValidationError('SKU already exists.')


class ProductTagSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class ProductListSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    nameAr = fields.Str()
    description = fields.Str()
    descriptionAr = fields.Str()
    short_description = fields.Str()
    short_descriptionAr = fields.Str()
    sku = fields.Str()
    price = fields.Decimal()
    compare_price = fields.Decimal()
    stock_quantity = fields.Int()
    is_active = fields.Bool()
    is_featured = fields.Bool()
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
                'name': obj.category.name,
                'nameAr': obj.category.nameAr,
                'slug': obj.category.slug
            }
        return None
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_review_count(self, obj):
        return obj.get_review_count()

class ProductDetailSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    nameAr = fields.Str()
    description = fields.Str()
    descriptionAr = fields.Str()
    short_description = fields.Str()
    short_descriptionAr = fields.Str()
    sku = fields.Str()
    price = fields.Decimal()
    compare_price = fields.Decimal()
    cost_price = fields.Decimal()
    stock_quantity = fields.Int()
    low_stock_threshold = fields.Int()
    weight = fields.Decimal()
    dimensions = fields.Str()
    is_active = fields.Bool()
    is_featured = fields.Bool()
    is_digital = fields.Bool()
    requires_shipping = fields.Bool()
    meta_title = fields.Str()
    meta_description = fields.Str()
    slug = fields.Str()
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
                'name': obj.category.name,
                'nameAr': obj.category.nameAr,
                'slug': obj.category.slug,
                'description': obj.category.description,
                'descriptionAr': obj.category.descriptionAr
            }
        return None
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()
    
    def get_review_count(self, obj):
        return obj.get_review_count()
