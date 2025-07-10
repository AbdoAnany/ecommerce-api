import unittest
import json
from tests.base import BaseTestCase
from app import db
from app.models import Category

class CategoryTestCase(BaseTestCase):
    """Test cases for category endpoints."""
    
    def test_get_all_categories(self):
        """Test getting all categories."""
        # Create a sample category
        self.create_sample_category()
        
        response = self.client.get('/api/v1/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_get_category_by_id(self):
        """Test getting a specific category by ID."""
        category = self.create_sample_category()
        
        response = self.client.get(f'/api/v1/categories/{category.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['id'], category.id)
        self.assertEqual(data['data']['name']['en'], category.name_en)
    
    def test_get_nonexistent_category(self):
        """Test getting a category that doesn't exist."""
        response = self.client.get('/api/v1/categories/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_create_category_admin(self):
        """Test creating a category as admin."""
        headers = self.get_admin_headers()
        
        category_data = {
            'name_en': 'New Category',
            'description_en': 'A new test category',
            'parent_id': None
        }
        
        response = self.client.post('/api/v1/categories',
                                  data=json.dumps(category_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['data']['name']['en'], 'New Category')
        self.assertIsNotNone(data['data']['slug'])
    
    def test_create_category_customer_forbidden(self):
        """Test that customers cannot create categories."""
        headers = self.get_customer_headers()
        
        category_data = {
            'name_en': 'New Category',
            'description_en': 'A new test category'
        }
        
        response = self.client.post('/api/v1/categories',
                                  data=json.dumps(category_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 403)
    
    def test_create_category_duplicate_name(self):
        """Test creating a category with duplicate name."""
        # Create first category
        self.create_sample_category()
        
        headers = self.get_admin_headers()
        
        category_data = {
            'name_en': 'Electronics',  # Same name as existing category
            'description_en': 'Duplicate category'
        }
        
        response = self.client.post('/api/v1/categories',
                                  data=json.dumps(category_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 400)
    
    def test_update_category(self):
        """Test updating a category."""
        category = self.create_sample_category()
        headers = self.get_admin_headers()
        
        update_data = {
            'name': 'Updated Electronics',
            'description': 'Updated description'
        }
        
        response = self.client.put(f'/api/v1/categories/{category.id}',
                                 data=json.dumps(update_data),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['name'], 'Updated Electronics')
        self.assertEqual(data['data']['description'], 'Updated description')
    
    def test_delete_category(self):
        """Test deleting a category."""
        category = self.create_sample_category()
        headers = self.get_admin_headers()
        
        response = self.client.delete(f'/api/v1/categories/{category.id}',
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify category is deleted
        response = self.client.get(f'/api/v1/categories/{category.id}')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_category_with_products_should_fail(self):
        """Test deleting a category that has products should fail."""
        category = self.create_sample_category()
        self.create_sample_product(category.id)
        
        headers = self.get_admin_headers()
        
        response = self.client.delete(f'/api/v1/categories/{category.id}',
                                    headers=headers)
        # Should fail because category has products
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
