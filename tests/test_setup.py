import unittest
import json
from tests.base import BaseTestCase

class SetupTestCase(BaseTestCase):
    """Test cases for setup and emergency endpoints."""
    
    def test_setup_health_check(self):
        """Test setup health check endpoint."""
        response = self.client.get('/setup/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('database', data)
    
    def test_list_users_setup(self):
        """Test listing users via setup endpoint."""
        response = self.client.get('/setup/list-users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)
        self.assertIsInstance(data['users'], list)
        # Should have at least admin and customer users
        self.assertGreaterEqual(len(data['users']), 2)
    
    def test_promote_user_by_id_setup(self):
        """Test promoting user by ID via setup endpoint."""
        promote_data = {
            'user_id': self.customer_user.id
        }
        
        response = self.client.post('/setup/promote-user',
                                  data=json.dumps(promote_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('promoted', data['message'])
    
    def test_promote_user_by_email_setup(self):
        """Test promoting user by email via setup endpoint."""
        promote_data = {
            'email': 'customer@test.com'
        }
        
        response = self.client.post('/setup/promote-user',
                                  data=json.dumps(promote_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('promoted', data['message'])
    
    def test_promote_nonexistent_user_setup(self):
        """Test promoting a user that doesn't exist."""
        promote_data = {
            'user_id': 9999
        }
        
        response = self.client.post('/setup/promote-user',
                                  data=json.dumps(promote_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
    
    def test_reset_admin_password_setup(self):
        """Test resetting admin password via setup endpoint."""
        reset_data = {
            'admin_email': 'admin@test.com',
            'new_password': 'newtestpassword'
        }
        
        response = self.client.post('/setup/reset-admin-password',
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # Verify new password works
        login_response = self.client.post('/api/v1/auth/login',
                                        data=json.dumps({
                                            'email': 'admin@test.com',
                                            'password': 'newtestpassword'
                                        }),
                                        content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
    
    def test_reset_nonexistent_admin_password(self):
        """Test resetting password for non-existent admin."""
        reset_data = {
            'admin_email': 'nonexistent@test.com',
            'new_password': 'newpassword'
        }
        
        response = self.client.post('/setup/reset-admin-password',
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
