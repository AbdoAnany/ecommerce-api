import unittest
import json
from tests.base import BaseTestCase
from app import db
from app.models import User, UserRole

class AdminTestCase(BaseTestCase):
    """Test cases for admin endpoints."""
    
    def test_admin_dashboard(self):
        """Test admin dashboard endpoint."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/dashboard', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('total_users', data['data'])
        self.assertIn('total_products', data['data'])
        self.assertIn('total_orders', data['data'])
    
    def test_admin_dashboard_customer_forbidden(self):
        """Test that customers cannot access admin dashboard."""
        headers = self.get_customer_headers()
        
        response = self.client.get('/api/v1/admin/dashboard', headers=headers)
        self.assertEqual(response.status_code, 403)
    
    def test_get_all_users(self):
        """Test getting all users as admin."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/users', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        # Should have at least admin and customer users
        self.assertGreaterEqual(len(data['data']), 2)
    
    def test_get_user_details(self):
        """Test getting specific user details as admin."""
        headers = self.get_admin_headers()
        
        response = self.client.get(f'/api/v1/admin/users/{self.customer_user.id}', 
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['id'], self.customer_user.id)
        self.assertEqual(data['data']['email'], 'customer@test.com')
    
    def test_update_user_status(self):
        """Test updating user status as admin."""
        headers = self.get_admin_headers()
        
        update_data = {
            'is_active': False,
            'is_verified': True
        }
        
        response = self.client.put(f'/api/v1/admin/users/{self.customer_user.id}',
                                 data=json.dumps(update_data),
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['is_active'], False)
        self.assertEqual(data['data']['is_verified'], True)
    
    def test_get_admin_users(self):
        """Test getting admin users list."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/admin-users', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        # Should have at least one admin user
        self.assertGreaterEqual(len(data['data']), 1)
        
        # Check that returned user is admin
        admin_users = [user for user in data['data'] if user['role'] == 'admin']
        self.assertGreater(len(admin_users), 0)
    
    def test_get_current_admin(self):
        """Test getting current admin details."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/current-admin', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['email'], 'admin@test.com')
        self.assertEqual(data['data']['role'], 'admin')
    
    def test_get_admin_stats(self):
        """Test getting admin statistics."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/admin-stats', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('total_admins', data['data'])
        self.assertIn('active_admins', data['data'])
    
    def test_promote_user_to_admin(self):
        """Test promoting a user to admin."""
        headers = self.get_admin_headers()
        
        response = self.client.put(f'/api/v1/admin/promote-user/{self.customer_user.id}',
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['role'], 'admin')
        
        # Verify user is now admin
        db.session.refresh(self.customer_user)
        self.assertEqual(self.customer_user.role, UserRole.ADMIN)
    
    def test_demote_admin_to_user(self):
        """Test demoting an admin to user."""
        # First promote customer to admin
        self.customer_user.role = UserRole.ADMIN
        db.session.commit()
        
        headers = self.get_admin_headers()
        
        response = self.client.put(f'/api/v1/admin/demote-admin/{self.customer_user.id}',
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['role'], 'customer')
        
        # Verify user is now customer
        db.session.refresh(self.customer_user)
        self.assertEqual(self.customer_user.role, UserRole.CUSTOMER)
    
    def test_bulk_promote_users(self):
        """Test bulk promoting users to admin."""
        # Create additional test user
        test_user = User(
            username='testuser',
            email='testuser@test.com',
            first_name='Test',
            last_name='User',
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        
        headers = self.get_admin_headers()
        
        bulk_data = {
            'user_ids': [self.customer_user.id, test_user.id]
        }
        
        response = self.client.post('/api/v1/admin/bulk-promote',
                                  data=json.dumps(bulk_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['promoted_count'], 2)
        
        # Verify users are now admins
        db.session.refresh(self.customer_user)
        db.session.refresh(test_user)
        self.assertEqual(self.customer_user.role, UserRole.ADMIN)
        self.assertEqual(test_user.role, UserRole.ADMIN)
    
    def test_reset_user_password(self):
        """Test resetting user password as admin."""
        headers = self.get_admin_headers()
        
        reset_data = {
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(f'/api/v1/admin/users/{self.customer_user.id}/reset-password',
                                  data=json.dumps(reset_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # Verify new password works
        login_response = self.client.post('/api/v1/auth/login',
                                        data=json.dumps({
                                            'email': 'customer@test.com',
                                            'password': 'newpassword123'
                                        }),
                                        content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
    
    def test_change_own_password(self):
        """Test admin changing their own password."""
        headers = self.get_admin_headers()
        
        change_data = {
            'current_password': 'admin123',
            'new_password': 'newadminpassword'
        }
        
        response = self.client.post('/api/v1/admin/change-password',
                                  data=json.dumps(change_data),
                                  headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # Verify new password works
        login_response = self.client.post('/api/v1/auth/login',
                                        data=json.dumps({
                                            'email': 'admin@test.com',
                                            'password': 'newadminpassword'
                                        }),
                                        content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
    
    def test_generate_secure_password(self):
        """Test generating a secure password."""
        headers = self.get_admin_headers()
        
        response = self.client.get('/api/v1/admin/generate-password', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('password', data['data'])
        self.assertGreaterEqual(len(data['data']['password']), 12)

if __name__ == '__main__':
    unittest.main()
