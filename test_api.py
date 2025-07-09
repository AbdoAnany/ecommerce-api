#!/usr/bin/env python3

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5001/api/v1"

class APITester:
    def __init__(self):
        self.access_token = None
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        response = requests.get("http://localhost:5001/ping")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    
    def test_api_info(self):
        """Test API info endpoint"""
        print("ℹ️ Testing API info...")
        response = requests.get(f"{BASE_URL}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data['name']} {data['version']}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    
    def test_register(self):
        """Test user registration"""
        print("📝 Testing user registration...")
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "test123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code == 201:
            result = response.json()
            self.access_token = result['data']['access_token']
            print("✅ Registration successful")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            if response.status_code == 400:
                # User might already exist, try login
                return self.test_login()
            return False
    
    def test_login(self):
        """Test user login"""
        print("🔐 Testing user login...")
        data = {
            "email": "customer@example.com",
            "password": "customer123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['data']['access_token']
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def test_get_profile(self):
        """Test get user profile"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        print("👤 Testing get profile...")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Profile retrieved: {result['data']['username']}")
            return True
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            return False
    
    def test_get_products(self):
        """Test get products"""
        print("🛍️ Testing get products...")
        response = requests.get(f"{BASE_URL}/products")
        
        if response.status_code == 200:
            result = response.json()
            count = len(result['data'])
            print(f"✅ Retrieved {count} products")
            return True
        else:
            print(f"❌ Get products failed: {response.status_code}")
            return False
    
    def test_get_categories(self):
        """Test get categories"""
        print("📂 Testing get categories...")
        response = requests.get(f"{BASE_URL}/categories")
        
        if response.status_code == 200:
            result = response.json()
            count = len(result['data'])
            print(f"✅ Retrieved {count} categories")
            return True
        else:
            print(f"❌ Get categories failed: {response.status_code}")
            return False
    
    def test_cart_operations(self):
        """Test cart operations"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Get cart
        print("🛒 Testing get cart...")
        response = requests.get(f"{BASE_URL}/cart", headers=headers)
        if response.status_code != 200:
            print(f"❌ Get cart failed: {response.status_code}")
            return False
        
        # Add item to cart
        print("➕ Testing add to cart...")
        data = {"product_id": 1, "quantity": 2}
        response = requests.post(f"{BASE_URL}/cart/add", json=data, headers=headers)
        if response.status_code == 200:
            print("✅ Item added to cart")
        else:
            print(f"❌ Add to cart failed: {response.status_code}")
            return False
        
        # Get updated cart
        response = requests.get(f"{BASE_URL}/cart", headers=headers)
        if response.status_code == 200:
            result = response.json()
            items = result['data']['total_items']
            print(f"✅ Cart has {items} items")
            return True
        else:
            print(f"❌ Get updated cart failed: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting API Tests...\n")
        
        tests = [
            self.test_health_check,
            self.test_api_info,
            self.test_register,
            self.test_get_profile,
            self.test_get_products,
            self.test_get_categories,
            self.test_cart_operations
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()  # Empty line between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}\n")
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed. Check server logs.")
            return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("API Tester for E-commerce Backend")
        print("Usage: python test_api.py")
        print("Make sure the server is running on http://localhost:5000")
        return
    
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
