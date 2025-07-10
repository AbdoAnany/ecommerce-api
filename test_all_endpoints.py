#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints systematically and generates a report
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "https://ecommerce-api-2owr.onrender.com"
TIMEOUT = 30

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.admin_token = None
        self.customer_token = None
        self.test_results = []
        self.admin_user_id = None
        self.customer_user_id = None
        self.product_id = None
        self.category_id = None
        self.order_id = None
        
    def log_result(self, endpoint, method, status, response_time, success, error=None, response_data=None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status,
            'response_time': response_time,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        # Print result
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {method:6} {endpoint:50} [{status}] ({response_time:.2f}s)")
        if error:
            print(f"    Error: {error}")
        
    def test_endpoint(self, method, endpoint, headers=None, data=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            success = response.status_code == expected_status
            response_data = None
            error = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text[:200] if response.text else None
                
            if not success:
                error = f"Expected {expected_status}, got {response.status_code}"
                if response_data:
                    error += f" - {response_data}"
                    
            self.log_result(endpoint, method, response.status_code, response_time, success, error, response_data)
            return response
            
        except requests.exceptions.Timeout:
            self.log_result(endpoint, method, 0, TIMEOUT, False, "Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            self.log_result(endpoint, method, 0, 0, False, "Connection error")
            return None
        except Exception as e:
            self.log_result(endpoint, method, 0, 0, False, str(e))
            return None
    
    def get_auth_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"} if token else {}
    
    def test_health_endpoints(self):
        """Test health and info endpoints"""
        print("\n🏥 Testing Health & Info Endpoints")
        print("=" * 60)
        
        self.test_endpoint("GET", "/ping")
        self.test_endpoint("GET", "/api/v1")
        self.test_endpoint("GET", "/setup/health")
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints")
        print("=" * 60)
        
        # Test admin login
        admin_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        response = self.test_endpoint("POST", "/api/v1/auth/login", data=admin_data)
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.admin_token = data['data']['access_token']
                self.admin_user_id = data['data']['user']['id']
                print(f"    💡 Admin token obtained: {self.admin_token[:20]}...")
            except:
                print("    ⚠️  Failed to extract admin token")
        
        # Test customer login
        customer_data = {
            "email": "customer@example.com",
            "password": "customer123"
        }
        response = self.test_endpoint("POST", "/api/v1/auth/login", data=customer_data)
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.customer_token = data['data']['access_token']
                self.customer_user_id = data['data']['user']['id']
                print(f"    💡 Customer token obtained: {self.customer_token[:20]}...")
            except:
                print("    ⚠️  Failed to extract customer token")
        
        # Test user registration
        register_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        self.test_endpoint("POST", "/api/v1/auth/register", data=register_data, expected_status=201)
        
        # Test profile endpoints (requires auth)
        if self.admin_token:
            headers = self.get_auth_headers(self.admin_token)
            self.test_endpoint("GET", "/api/v1/auth/me", headers=headers)
            
            # Test profile update
            profile_data = {"first_name": "Updated", "last_name": "Admin"}
            self.test_endpoint("PUT", "/api/v1/auth/profile", headers=headers, data=profile_data)
    
    def test_products(self):
        """Test product endpoints"""
        print("\n📦 Testing Product Endpoints")
        print("=" * 60)
        
        # Test get all products
        response = self.test_endpoint("GET", "/api/v1/products")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    self.product_id = data['data'][0]['id']
                    print(f"    💡 Found product ID: {self.product_id}")
            except:
                pass
        
        # Test product pagination
        self.test_endpoint("GET", "/api/v1/products?page=1&per_page=5")
        
        # Test product search
        self.test_endpoint("GET", "/api/v1/products?search=iPhone")
        
        # Test get product by ID
        if self.product_id:
            self.test_endpoint("GET", f"/api/v1/products/{self.product_id}")
        
        # Test admin product operations
        if self.admin_token:
            headers = self.get_auth_headers(self.admin_token)
            
            # Test create product
            product_data = {
                "name_en": f"Test Product {int(time.time())}",
                "description_en": "Test product description",
                "price": 99.99,
                "stock_quantity": 50,
                "category_id": 20,  # Use existing category ID from the test
                "sku": f"TEST-{int(time.time())}"
            }
            response = self.test_endpoint("POST", "/api/v1/products", headers=headers, data=product_data, expected_status=201)
            
            # Test update product
            if self.product_id:
                update_data = {"name_en": "Updated Product Name", "price": 109.99}
                self.test_endpoint("PUT", f"/api/v1/products/{self.product_id}", headers=headers, data=update_data)
    
    def test_categories(self):
        """Test category endpoints"""
        print("\n📁 Testing Category Endpoints")
        print("=" * 60)
        
        # Test get all categories
        response = self.test_endpoint("GET", "/api/v1/categories")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    self.category_id = data['data'][0]['id']
                    print(f"    💡 Found category ID: {self.category_id}")
            except:
                pass
        
        # Test get category by ID
        if self.category_id:
            self.test_endpoint("GET", f"/api/v1/categories/{self.category_id}")
        
        # Test admin category operations
        if self.admin_token:
            headers = self.get_auth_headers(self.admin_token)
            
            # Test create category
            category_data = {
                "name_en": f"Test Category {int(time.time())}",
                "description_en": "Test category description",
                "slug": f"test-category-{int(time.time())}"
            }
            self.test_endpoint("POST", "/api/v1/categories", headers=headers, data=category_data, expected_status=201)
    
    def test_shopping_cart(self):
        """Test shopping cart endpoints"""
        print("\n🛒 Testing Shopping Cart Endpoints")
        print("=" * 60)
        
        if not self.customer_token:
            print("    ⚠️  Skipping cart tests - no customer token")
            return
        
        headers = self.get_auth_headers(self.customer_token)
        
        # Test get cart
        self.test_endpoint("GET", "/api/v1/cart", headers=headers)
        
        # Test add item to cart
        if self.product_id:
            cart_data = {"product_id": self.product_id, "quantity": 2}
            self.test_endpoint("POST", "/api/v1/cart/add", headers=headers, data=cart_data, expected_status=201)
        
        # Test get cart after adding item
        self.test_endpoint("GET", "/api/v1/cart", headers=headers)
    
    def test_admin_dashboard(self):
        """Test admin dashboard endpoints"""
        print("\n👑 Testing Admin Dashboard Endpoints")
        print("=" * 60)
        
        if not self.admin_token:
            print("    ⚠️  Skipping admin tests - no admin token")
            return
        
        headers = self.get_auth_headers(self.admin_token)
        
        # Test dashboard stats
        self.test_endpoint("GET", "/api/v1/admin/dashboard", headers=headers)
        
        # Test get all users
        self.test_endpoint("GET", "/api/v1/admin/users", headers=headers)
        
        # Test admin user management
        self.test_endpoint("GET", "/api/v1/admin/admin-users", headers=headers)
        self.test_endpoint("GET", "/api/v1/admin/current-admin", headers=headers)
        self.test_endpoint("GET", "/api/v1/admin/admin-stats", headers=headers)
        
        # Test password management
        self.test_endpoint("GET", "/api/v1/admin/generate-password", headers=headers)
        
        # Test get all orders
        self.test_endpoint("GET", "/api/v1/admin/orders", headers=headers)
    
    def test_setup_endpoints(self):
        """Test setup and emergency endpoints"""
        print("\n🔧 Testing Setup & Emergency Endpoints")
        print("=" * 60)
        
        # Test list users
        self.test_endpoint("GET", "/setup/list-users")
        
        # Test emergency admin reset (might be disabled in production)
        reset_data = {"admin_email": "admin@example.com", "new_password": "admin123"}
        self.test_endpoint("POST", "/setup/reset-admin-password", data=reset_data)
        
        # Test database initialization (might be disabled)
        self.test_endpoint("POST", "/setup/init-db")
    
    def test_user_management(self):
        """Test user management endpoints"""
        print("\n👥 Testing User Management Endpoints")
        print("=" * 60)
        
        if not self.customer_token:
            print("    ⚠️  Skipping user management tests - no customer token")
            return
        
        headers = self.get_auth_headers(self.customer_token)
        
        # Test user profile
        self.test_endpoint("GET", "/api/v1/users/profile", headers=headers)
        
        # Test user orders
        self.test_endpoint("GET", "/api/v1/users/orders", headers=headers)
        
        # Test user dashboard
        self.test_endpoint("GET", "/api/v1/users/dashboard", headers=headers)
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Comprehensive API Endpoint Testing")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Timeout: {TIMEOUT}s")
        print()
        
        start_time = time.time()
        
        # Run all test categories
        self.test_health_endpoints()
        self.test_authentication()
        self.test_products()
        self.test_categories()
        self.test_shopping_cart()
        self.test_admin_dashboard()
        self.test_setup_endpoints()
        self.test_user_management()
        
        total_time = time.time() - start_time
        
        # Generate summary report
        self.generate_report(total_time)
    
    def generate_report(self, total_time):
        """Generate test summary report"""
        print("\n📊 TEST SUMMARY REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        # Group by status code
        status_codes = {}
        for result in self.test_results:
            status = result['status_code']
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print(f"\nStatus Code Distribution:")
        for status, count in sorted(status_codes.items()):
            print(f"  {status}: {count}")
        
        # Show failed endpoints
        if failed_tests > 0:
            print(f"\n❌ FAILED ENDPOINTS ({failed_tests}):")
            print("-" * 60)
            for result in self.test_results:
                if not result['success']:
                    print(f"  {result['method']:6} {result['endpoint']:40} [{result['status_code']}]")
                    if result['error']:
                        print(f"         Error: {result['error']}")
        
        # Show successful critical endpoints
        critical_endpoints = [
            "/setup/health",
            "/api/v1/auth/login",
            "/api/v1/products",
            "/api/v1/admin/dashboard"
        ]
        
        print(f"\n✅ CRITICAL ENDPOINTS STATUS:")
        print("-" * 60)
        for endpoint in critical_endpoints:
            matching_results = [r for r in self.test_results if endpoint in r['endpoint']]
            if matching_results:
                result = matching_results[0]
                status_icon = "✅" if result['success'] else "❌"
                print(f"  {status_icon} {endpoint:40} [{result['status_code']}]")
            else:
                print(f"  ⚪ {endpoint:40} [NOT TESTED]")
        
        # Authentication status
        print(f"\n🔑 AUTHENTICATION STATUS:")
        print("-" * 60)
        print(f"  Admin Token: {'✅ Obtained' if self.admin_token else '❌ Failed'}")
        print(f"  Customer Token: {'✅ Obtained' if self.customer_token else '❌ Failed'}")
        
        # Save detailed report to file
        self.save_detailed_report()
    
    def save_detailed_report(self):
        """Save detailed test results to JSON file"""
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_tests': len(self.test_results),
                'successful_tests': sum(1 for r in self.test_results if r['success']),
                'admin_token_obtained': bool(self.admin_token),
                'customer_token_obtained': bool(self.customer_token)
            },
            'test_results': self.test_results
        }
        
        filename = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {filename}")

def main():
    tester = APITester(BASE_URL)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
