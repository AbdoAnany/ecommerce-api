#!/usr/bin/env python3
"""
Monitor Render deployment and test when ready
"""
import requests
import time
import sys
from datetime import datetime

def check_render_status(url):
    """Check if the Render service is responding"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

def monitor_deployment(url, max_wait=600):  # 10 minutes max
    """Monitor deployment until it's ready or timeout"""
    start_time = datetime.now()
    attempts = 0
    
    print(f"🔍 Monitoring deployment: {url}")
    print(f"⏰ Started at: {start_time.strftime('%H:%M:%S')}")
    print("=" * 60)
    
    while True:
        attempts += 1
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if elapsed > max_wait:
            print(f"\n⏰ Timeout reached ({max_wait}s). Deployment may still be in progress.")
            break
            
        print(f"\n🔍 Attempt {attempts} ({elapsed:.0f}s elapsed)")
        
        is_ready, result = check_render_status(url)
        
        if is_ready:
            print(f"✅ Deployment successful!")
            print(f"📊 Health data: {result}")
            print(f"⏱️  Total time: {elapsed:.0f} seconds")
            return True
        else:
            print(f"⏳ Not ready yet: {result}")
            
        if attempts % 6 == 0:  # Every minute
            print(f"💡 Still waiting... ({elapsed:.0f}s elapsed)")
            
        time.sleep(10)  # Wait 10 seconds between checks
    
    return False

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: python3 monitor_deployment.py <render-url>")
        print("Example: python3 monitor_deployment.py https://ecommerce-api-abc123.onrender.com")
        return
    
    print("🚀 Render Deployment Monitor")
    print("===========================")
    print(f"URL: {url}")
    print(f"Fix applied: psycopg2-binary for Python 3.11 compatibility")
    print("")
    
    success = monitor_deployment(url)
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test API endpoints with Postman collection")
        print("2. Check admin panel access")
        print("3. Verify database connectivity")
        print(f"\n🌐 Your API is live at: {url}")
    else:
        print("\n⚠️  Deployment monitoring timed out")
        print("\n🔧 Troubleshooting:")
        print("1. Check Render dashboard for build logs")
        print("2. Verify environment variables are set")
        print("3. Check database connection")
        print("4. Try manual health check later")

if __name__ == "__main__":
    main()
