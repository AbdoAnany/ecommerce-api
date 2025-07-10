#!/usr/bin/env python3
"""
Check admin user status and test login
"""
import requests
import json

BASE_URL = "https://ecommerce-api-2owr.onrender.com"

def check_admin_user():
    """Check if admin user exists and can login"""
    print("🔍 Checking Admin User Status")
    print("=" * 40)
    
    # Try to login with admin credentials
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Admin login successful!")
            print(f"📧 Email: {login_data['email']}")
            print(f"🔑 Token received: Yes")
            
            # Test admin profile
            token = auth_data.get('access_token')
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = requests.get(
                    f"{BASE_URL}/api/v1/users/profile",
                    headers=headers,
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"👤 Username: {profile_data.get('username', 'N/A')}")
                    print(f"🏷️ Role: {profile_data.get('role', 'N/A')}")
                    print(f"📧 Email: {profile_data.get('email', 'N/A')}")
                    print(f"✅ Admin verification: {'admin' in profile_data.get('role', '').lower()}")
                
        elif response.status_code == 401:
            print("❌ Admin login failed - Invalid credentials")
            print("   This means admin user may not exist or password is different")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")

def check_database_status():
    """Check if database is initialized"""
    print("\n🗄️ Checking Database Status")
    print("=" * 40)
    
    try:
        # Check health
        response = requests.get(f"{BASE_URL}/setup/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"📊 Database: {health_data.get('database', 'unknown')}")
            print(f"💚 Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"⚠️ Health check failed: {response.status_code}")
            
        # Check products (indicates if DB is initialized)
        response = requests.get(f"{BASE_URL}/api/v1/products", timeout=10)
        if response.status_code == 200:
            products = response.json()
            print(f"📦 Products available: {len(products) if isinstance(products, list) else 'Error'}")
        else:
            print(f"📦 Products endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def main():
    print("🔐 Admin User Checker")
    print("=" * 50)
    print(f"🌐 API: {BASE_URL}")
    print()
    
    check_database_status()
    check_admin_user()
    
    print("\n" + "=" * 50)
    print("📋 Admin Access Information:")
    print("   Web Panel: https://ecommerce-api-2owr.onrender.com/admin")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    print("   Role: admin")
    print()
    print("💡 If admin login fails, run database initialization:")
    print("   curl -X POST https://ecommerce-api-2owr.onrender.com/setup/init-db")

if __name__ == "__main__":
    main()
