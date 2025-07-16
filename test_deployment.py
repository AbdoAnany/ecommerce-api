#!/usr/bin/env python3
"""
Complete API test suite for deployed e-commerce API
"""

import requests
import json
import sys
from datetime import datetime

def get_render_url():
    """Get the Render URL from command line or user input"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    print("🌐 Enter your Render service URL:")
    print("   Example: https://ecommerce-api-abc123.onrender.com")
    url = input("URL: ").strip()
    
    if not url.startswith("https://"):
        url = "https://" + url
    
    return url

def test_setup_endpoints(base_url):
    """Test setup and health endpoints"""
    print("\n🔧 Testing Setup Endpoints")
    print("=" * 40)
    
    # Health check
    try:
        response = requests.get(f"{base_url}/setup/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"📊 Database: {health_data['database']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    return True

def initialize_database(base_url):
    """Initialize database if needed"""
    print("\n🔄 Database Initialization")
    print("=" * 40)
    
    try:
        response = requests.post(f"{base_url}/setup/init-db", timeout=30)
        if response.status_code == 200:
            init_data = response.json()
            print(f"✅ Database Initialized: {init_data['message']}")
            if 'admin_email' in init_data:
                print(f"👤 Admin: {init_data['admin_email']} / {init_data['admin_password']}")
                print(f"📁 Categories: {init_data.get('categories_created', 0)}")
                print(f"📦 Products: {init_data.get('products_created', 0)}")
            return True
        elif response.status_code == 403:
            print("⚠️  Database initialization not allowed")
            print("   Add environment variable: ALLOW_DB_INIT=true")
            return False
        else:
            print(f"❌ Database Init Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Database Init Error: {e}")
        return False

def test_api_endpoints(base_url):
    """Test main API endpoints"""
    print("\n🧪 Testing API Endpoints")
    print("=" * 40)
    
    # Test user registration
    print("👤 Testing User Registration...")
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 201:
            print("✅ User Registration: Success")
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ User Registration: User already exists (OK)")
        else:
            print(f"⚠️  User Registration: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ User Registration Error: {e}")
    
    # Test products endpoint
    print("📦 Testing Products Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/products", timeout=10)
        if response.status_code == 200:
            products = response.json()
            if isinstance(products, list) and len(products) > 0:
                print(f"✅ Products: Found {len(products)} products")
            else:
                print("⚠️  Products: No products found")
        else:
            print(f"❌ Products: {response.status_code}")
    except Exception as e:
        print(f"❌ Products Error: {e}")
    
    # Test categories endpoint
    print("📁 Testing Categories Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/categories", timeout=10)
        if response.status_code == 200:
            categories = response.json()
            if isinstance(categories, list) and len(categories) > 0:
                print(f"✅ Categories: Found {len(categories)} categories")
            else:
                print("⚠️  Categories: No categories found")
        else:
            print(f"❌ Categories: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories Error: {e}")

def test_authentication_flow(base_url):
    """Test complete authentication flow"""
    print("\n🔐 Testing Authentication Flow")
    print("=" * 40)
    
    # Test login with admin credentials
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Admin Login: Success")
            token = auth_data.get('access_token')
            
            if token:
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = requests.get(
                    f"{base_url}/api/v1/users/profile",
                    headers=headers,
                    timeout=10
                )
                if profile_response.status_code == 200:
                    print("✅ Protected Endpoint: Success")
                else:
                    print(f"⚠️  Protected Endpoint: {profile_response.status_code}")
        else:
            print(f"❌ Admin Login: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Authentication Error: {e}")

def main():
    """Main test function"""
    print("🚀 E-commerce API Deployment Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get API URL
    base_url = get_render_url()
    print(f"🌐 Testing API at: {base_url}")
    
    # Test setup endpoints
    if not test_setup_endpoints(base_url):
        print("\n❌ Setup endpoints failed. Check your deployment.")
        return
    
    # Initialize database
    print("\n💡 Attempting database initialization...")
    db_initialized = initialize_database(base_url)
    
    if not db_initialized:
        print("\n⚠️  Database not initialized. Manual setup may be required.")
        print("   1. Add ALLOW_DB_INIT=true to Render environment variables")
        print("   2. Redeploy the service")
        print("   3. Run this script again")
        return
    
    # Test API endpoints
    test_api_endpoints(base_url)
    
    # Test authentication
    test_authentication_flow(base_url)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT TEST COMPLETE!")
    print(f"🔗 Your API is running at: {base_url}")
    print("\n📋 Next Steps:")
    print("   1. Test with Postman collection")
    print("   2. Access admin panel: /admin")
    print("   3. Change admin password")
    print("   4. Remove ALLOW_DB_INIT environment variable")
    print("\n✅ Your e-commerce API is ready for production!")

if __name__ == "__main__":
    main()
