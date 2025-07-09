#!/usr/bin/env python3
"""
Script to check deployment status and test the API endpoints
"""
import requests
import time
import json
import sys
from datetime import datetime

def get_render_url():
    """Get the Render URL from user input if not provided"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    print("🌐 Please provide your Render service URL")
    print("   You can find this in your Render dashboard after creating the service")
    print("   Example: https://ecommerce-api-abc123.onrender.com")
    print("")
    url = input("Enter your Render URL: ").strip()
    
    if not url.startswith("https://"):
        url = "https://" + url
    
    return url

# Get Render URL
RENDER_URL = get_render_url()

def check_health():
    """Check if the API is responding"""
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def test_basic_endpoints():
    """Test basic API endpoints"""
    endpoints = [
        "/",
        "/health",
        "/api/auth/register",  # This should return method not allowed for GET
        "/api/products",
        "/api/categories"
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RENDER_URL}{endpoint}", timeout=10)
            results[endpoint] = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code in [200, 405]  # 405 is expected for POST-only endpoints
            }
        except requests.exceptions.RequestException as e:
            results[endpoint] = {
                "error": str(e),
                "success": False
            }
    
    return results

def main():
    print(f"🚀 Checking deployment status for: {RENDER_URL}")
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check health endpoint
    print("🔍 Checking health endpoint...")
    is_healthy, health_data = check_health()
    
    if is_healthy:
        print("✅ API is healthy!")
        print(f"📊 Health data: {json.dumps(health_data, indent=2)}")
    else:
        print(f"❌ API health check failed: {health_data}")
        print("\n💡 This might indicate the deployment is still in progress or failed.")
        return
    
    print("\n" + "=" * 60)
    print("🧪 Testing basic endpoints...")
    
    # Test endpoints
    test_results = test_basic_endpoints()
    
    for endpoint, result in test_results.items():
        if result.get("success", False):
            status = "✅"
            response_time = result.get("response_time", 0)
            print(f"{status} {endpoint} - {result['status_code']} ({response_time:.2f}s)")
        else:
            status = "❌"
            error = result.get("error", f"Status: {result.get('status_code', 'unknown')}")
            print(f"{status} {endpoint} - {error}")
    
    print("\n" + "=" * 60)
    print("📝 Summary:")
    
    successful_tests = sum(1 for result in test_results.values() if result.get("success", False))
    total_tests = len(test_results)
    
    if is_healthy and successful_tests == total_tests:
        print("🎉 All tests passed! Deployment is successful.")
        print("\n📚 Next steps:")
        print("1. Check your Render dashboard for deployment logs")
        print("2. Test API endpoints using the provided Postman collection")
        print("3. Verify database connectivity by creating a user and product")
    elif is_healthy:
        print(f"⚠️  Partial success: {successful_tests}/{total_tests} endpoints working")
        print("   The API is running but some endpoints may need investigation")
    else:
        print("💥 Deployment appears to have issues")
        print("   Check Render logs for error details")
    
    print(f"\n🔗 API URL: {RENDER_URL}")
    print("📖 Full documentation: README.md")

if __name__ == "__main__":
    main()
