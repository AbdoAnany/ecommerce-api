from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Category

class CategoryCreateSchema(Schema):
    name_en = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    name_ar = fields.Str(validate=validate.Length(max=100))
    description_en = fields.Str()
    description_ar = fields.Str()
    slug_en = fields.Str(validate=validate.Length(max=100))
    slug_ar = fields.Str(validate=validate.Length(max=100))
    slug = fields.Str(validate=validate.Length(max=100))  # Primary slug for compatibility
    thumbnail = fields.Str(validate=validate.Length(max=500))
    image_url = fields.Str(validate=validate.Length(max=255))  # Backward compatibility
    is_active = fields.Bool()
    is_featured = fields.Bool()
    position = fields.Int(validate=validate.Range(min=0))
    sort_order = fields.Int(validate=validate.Range(min=0))  # Backward compatibility
    parent_id = fields.Int(allow_none=True)
    type = fields.Str(validate=validate.Length(max=50))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'draft']))
    
    @validates('slug')
    def validate_slug(self, value):
        if value:
            existing_category = Category.query.filter_by(slug=value).first()
            if existing_category:
                raise ValidationError('Slug already exists.')
    
    @validates('parent_id')
    def validate_parent_id(self, value):
        if value is not None:
            parent_category = Category.query.get(value)
            if not parent_category:
                raise ValidationError('Parent category does not exist.')

class CategoryUpdateSchema(Schema):
    name_en = fields.Str(validate=validate.Length(min=1, max=100))
    name_ar = fields.Str(validate=validate.Length(max=100))
    description_en = fields.Str()
    description_ar = fields.Str()
    slug_en = fields.Str(validate=validate.Length(max=100))
    slug_ar = fields.Str(validate=validate.Length(max=100))
    slug = fields.Str(validate=validate.Length(max=100))
    thumbnail = fields.Str(validate=validate.Length(max=500))
    image_url = fields.Str(validate=validate.Length(max=255))
    is_active = fields.Bool()
    is_featured = fields.Bool()
    position = fields.Int(validate=validate.Range(min=0))
    sort_order = fields.Int(validate=validate.Range(min=0))
    parent_id = fields.Int(allow_none=True)
    type = fields.Str(validate=validate.Length(max=50))
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'draft']))
    
    @validates('slug')
    def validate_slug(self, value):
        if value:
            category_id = self.context.get('category_id')
            existing_category = Category.query.filter_by(slug=value).first()
            if existing_category and existing_category.id != category_id:
                raise ValidationError('Slug already exists.')
    
    @validates('parent_id')
    def validate_parent_id(self, value):
        if value is not None:
            category_id = self.context.get('category_id')
            if value == category_id:
                raise ValidationError('Category cannot be its own parent.')
            
            parent_category = Category.query.get(value)
            if not parent_category:
                raise ValidationError('Parent category does not exist.')

class CategoryListSchema(Schema):
    id = fields.Int()
    name_en = fields.Str()
    name_ar = fields.Str()
    slug_en = fields.Str()
    slug_ar = fields.Str()
    slug = fields.Str()
    thumbnail = fields.Str()
    is_active = fields.Bool()
    is_featured = fields.Bool()
    position = fields.Int()
    type = fields.Str()
    status = fields.Str()
    children_count = fields.Method('get_children_count')
    product_count = fields.Method('get_product_count')
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    def get_children_count(self, obj):
        return obj.get_children_count()
    
    def get_product_count(self, obj):
        return obj.get_product_count()

class CategoryDetailSchema(Schema):
    id = fields.Int()
    name = fields.Method('get_name_dict')
    slug = fields.Method('get_slug_dict')
    thumbnail = fields.Str()
    parent = fields.Method('get_parent')
    breadcrumbs = fields.Method('get_breadcrumbs')
    meta = fields.Method('get_meta')
    children_count = fields.Method('get_children_count')
    is_featured = fields.Bool()
    position = fields.Int()
    type = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    def get_name_dict(self, obj):
        return {
            'en': obj.name_en,
            'ar': obj.name_ar or obj.name_en
        }
    
    def get_slug_dict(self, obj):
        return {
            'en': obj.slug_en or obj.slug,
            'ar': obj.slug_ar or obj.slug_en or obj.slug
        }
    
    def get_parent(self, obj):
        if obj.parent:
            return {
                'id': str(obj.parent.id),
                'name': {
                    'en': obj.parent.name_en,
                    'ar': obj.parent.name_ar or obj.parent.name_en
                }
            }
        return None
    
    def get_breadcrumbs(self, obj):
        return obj.get_breadcrumbs()
    
    def get_meta(self, obj):
        return {
            'product_count': obj.get_product_count(),
            'stock_total': obj.get_stock_total()
        }
    
    def get_children_count(self, obj):
        return obj.get_children_count()

class CategoryTreeSchema(Schema):
    """Schema for hierarchical category tree"""
    id = fields.Int()
    name = fields.Method('get_name_dict')
    slug = fields.Method('get_slug_dict')
    thumbnail = fields.Str()
    is_featured = fields.Bool()
    position = fields.Int()
    children = fields.Method('get_children')
    product_count = fields.Method('get_product_count')
    
    def get_name_dict(self, obj):
        return {
            'en': obj.name_en,
            'ar': obj.name_ar or obj.name_en
        }
    
    def get_slug_dict(self, obj):
        return {
            'en': obj.slug_en or obj.slug,
            'ar': obj.slug_ar or obj.slug_en or obj.slug
        }
    
    def get_children(self, obj):
        if obj.children:
            return CategoryTreeSchema(many=True).dump([child for child in obj.children if child.is_active])
        return []
    
    def get_product_count(self, obj):
        return obj.get_product_count()
