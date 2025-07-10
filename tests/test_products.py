import unittest
import json
from tests.base import BaseTestCase
from app import db
from app.models import Product

class ProductTestCase(BaseTestCase):
    """Test cases for product endpoints."""
    
    def test_get_all_products(self):
        """Test getting all products."""
        # Create a sample product
        self.create_sample_product()
        
        response = self.client.get('/api/v1/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
    
    def test_get_products_with_pagination(self):
        """Test getting products with pagination."""
        # Create multiple products
        for i in range(5):
            category = self.create_sample_category(f'Category{i}', f'category-{i}')
            product = Product(
                name_en=f'Test Product {i}',
                description_en=f'Test product {i} description',
                sku=f'TEST-00{i}',
                slug=f'test-product-{i}',
                price=99.99 + i,
                stock_quantity=10,
                category_id=category.id,
                is_active=True
            )
            db.session.add(product)
        db.session.commit()
        
        response = self.client.get('/api/v1/products?page=1&per_page=3')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('pagination', data)
        self.assertLessEqual(len(data['data']), 3)
    
    def test_get_product_by_id(self):
        """Test getting a specific product by ID."""
        product = self.create_sample_product()
        
        response = self.client.get(f'/api/v1/products/{product.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['id'], product.id)
        self.assertEqual(data['data']['name_en'], product.name_en)
    
    def test_get_nonexistent_product(self):
        """Test getting a product that doesn't exist."""
        response = self.client.get('/api/v1/products/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_search_products(self):
        """Test searching products."""
        # Create products with different names
        electronics_cat = self.create_sample_category('Electronics', 'electronics')
        phones_cat = self.create_sample_category('Phones', 'phones')
        
        product1 = Product(
            name_en='iPhone 15',
            description_en='Apple smartphone',
            sku='IPHONE-001',
            slug='iphone-15',
            price=999.99,
            stock_quantity=10,
            category_id=electronics_cat.id,
            is_active=True
        )
        
        product2 = Product(
            name_en='Samsung Galaxy',
            description_en='Android smartphone',
            sku='SAMSUNG-001',
            slug='samsung-galaxy',
            price=899.99,
            stock_quantity=15,
            category_id=phones_cat.id,
            is_active=True
        )
        
        db.session.add(product1)
        db.session.add(product2)
        db.session.commit()
        
        # Search for iPhone
        response = self.client.get('/api/v1/products?search=iPhone')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data['data']), 0)
        
        # Check that iPhone product is in results
        product_names = [p['name_en'] for p in data['data']]
        self.assertIn('iPhone 15', product_names)
    
    def test_create_product_admin(self):
        """Test creating a product as admin."""
        category = self.create_sample_category()
        headers = self.get_admin_headers()
        
        product_data = {
            'name_en': 'New Test Product',
            'description_en': 'A new test product',
            'sku': 'NEW-TEST-001',
            'price': 149.99,
            'stock_quantity': 20,
            'category_id': category.id,
            'tags': ['new', 'test']
        }
        
        response = self.client.post('/api/v1/products',
                                  data=json.dumps(product_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['data']['name_en'], 'New Test Product')
        self.assertIsNotNone(data['data']['slug'])
    
    def test_create_product_customer_forbidden(self):
        """Test that customers cannot create products."""
        category = self.create_sample_category()
        headers = self.get_customer_headers()
        
        product_data = {
            'name_en': 'New Test Product',
            'description_en': 'A new test product',
            'sku': 'NEW-TEST-001',
            'price': 149.99,
            'stock_quantity': 20,
            'category_id': category.id
        }
        
        response = self.client.post('/api/v1/products',
                                  data=json.dumps(product_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 403)
    
    def test_create_product_invalid_category(self):
        """Test creating a product with invalid category."""
        headers = self.get_admin_headers()
        
        product_data = {
            'name_en': 'New Test Product',
            'description_en': 'A new test product',
            'sku': 'NEW-TEST-001',
            'price': 149.99,
            'stock_quantity': 20,
            'category_id': 9999  # Non-existent category
        }
        
        response = self.client.post('/api/v1/products',
                                  data=json.dumps(product_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 400)
    
    def test_update_product(self):
        """Test updating a product."""
        product = self.create_sample_product()
        headers = self.get_admin_headers()
        
        update_data = {
            'name_en': 'Updated Product Name',
            'price': 199.99,
            'stock_quantity': 15
        }
        
        response = self.client.put(f'/api/v1/products/{product.id}',
                                 data=json.dumps(update_data),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['name_en'], 'Updated Product Name')
        self.assertEqual(float(data['data']['price']), 199.99)
    
    def test_delete_product(self):
        """Test deleting a product."""
        product = self.create_sample_product()
        headers = self.get_admin_headers()
        
        response = self.client.delete(f'/api/v1/products/{product.id}',
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify product is deleted
        response = self.client.get(f'/api/v1/products/{product.id}')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
