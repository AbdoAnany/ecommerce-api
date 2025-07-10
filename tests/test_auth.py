import unittest
import json
from tests.base import BaseTestCase

class AuthTestCase(BaseTestCase):
    """Test cases for authentication endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
    
    def test_api_info(self):
        """Test the API info endpoint."""
        response = self.client.get('/api/v1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('name', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
    
    def test_admin_login_success(self):
        """Test successful admin login."""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'email': 'admin@test.com',
                                      'password': 'admin123'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertEqual(data['data']['user']['role'], 'admin')
    
    def test_customer_login_success(self):
        """Test successful customer login."""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'email': 'customer@test.com',
                                      'password': 'customer123'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data['data'])
        self.assertIn('refresh_token', data['data'])
        self.assertEqual(data['data']['user']['role'], 'customer')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'email': 'admin@test.com',
                                      'password': 'wrongpassword'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_missing_email(self):
        """Test login with missing email."""
        response = self.client.post('/api/v1/auth/login',
                                  data=json.dumps({
                                      'password': 'admin123'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post('/api/v1/auth/register',
                                  data=json.dumps({
                                      'username': 'newuser',
                                      'email': 'newuser@test.com',
                                      'password': 'newuser123',
                                      'first_name': 'New',
                                      'last_name': 'User',
                                      'phone': '+1234567890'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data['data'])
        self.assertEqual(data['data']['user']['username'], 'newuser')
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        response = self.client.post('/api/v1/auth/register',
                                  data=json.dumps({
                                      'username': 'newadmin',
                                      'email': 'admin@test.com',  # Already exists
                                      'password': 'newuser123',
                                      'first_name': 'New',
                                      'last_name': 'Admin'
                                  }),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_get_current_user(self):
        """Test getting current user profile."""
        headers = self.get_admin_headers()
        response = self.client.get('/api/v1/auth/me', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['email'], 'admin@test.com')
        self.assertEqual(data['data']['role'], 'admin')
    
    def test_get_profile(self):
        """Test getting user profile via profile endpoint."""
        headers = self.get_admin_headers()
        response = self.client.get('/api/v1/auth/profile', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['email'], 'admin@test.com')
    
    def test_update_profile(self):
        """Test updating user profile."""
        headers = self.get_customer_headers()
        response = self.client.put('/api/v1/auth/profile',
                                 data=json.dumps({
                                     'first_name': 'Updated',
                                     'last_name': 'Customer',
                                     'phone': '+9876543210'
                                 }),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['first_name'], 'Updated')
        self.assertEqual(data['data']['last_name'], 'Customer')
    
    def test_logout(self):
        """Test user logout."""
        headers = self.get_admin_headers()
        response = self.client.post('/api/v1/auth/logout', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/api/v1/auth/me')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
