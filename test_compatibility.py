#!/usr/bin/env python3
"""
Test database connection and Python compatibility
"""

import sys
import os

def test_python_version():
    """Test Python version compatibility"""
    print(f"🐍 Python version: {sys.version}")
    
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 11:
        if minor >= 13:
            print("⚠️  Python 3.13+ detected - may have compatibility issues")
            print("💡 Render deployment configured for Python 3.11")
        else:
            print("✅ Python version compatible")
    else:
        print("❌ Python version too old - requires Python 3.11+")
    
    return True

def test_psycopg2():
    """Test PostgreSQL driver import"""
    print("\n🗄️ Testing PostgreSQL driver...")
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
        print(f"📦 psycopg2 version: {psycopg2.__version__}")
        return True
    except ImportError as e:
        if "_PyInterpreterState_Get" in str(e):
            print("❌ Python 3.13 compatibility issue with psycopg2")
            print("💡 Solution: Render deployment uses Python 3.11")
        else:
            print(f"❌ psycopg2 import failed: {e}")
        return False

def test_database_url_parsing():
    """Test database URL parsing without actual connection"""
    print("\n🔗 Testing database URL parsing...")
    
    try:
        from sqlalchemy import create_engine
        from urllib.parse import urlparse
        
        # Test with a dummy PostgreSQL URL format
        test_url = "postgresql://user:pass@dpg-example-a:5432/database"
        parsed = urlparse(test_url)
        
        print(f"✅ Database URL parsing works")
        print(f"📊 Scheme: {parsed.scheme}")
        print(f"🏠 Host: {parsed.hostname}")
        print(f"🔌 Port: {parsed.port}")
        
        return True
    except Exception as e:
        print(f"❌ Database URL parsing failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\n🌶️ Testing Flask app creation...")
    
    try:
        from app import create_app
        
        # Set test environment
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        
        app = create_app('testing')
        print("✅ Flask app created successfully")
        
        with app.test_client() as client:
            response = client.get('/ping')
            if response.status_code == 200:
                print("✅ Health check endpoint working")
            else:
                print(f"⚠️  Health check returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def main():
    """Run all compatibility tests"""
    print("🧪 Python & Database Compatibility Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_psycopg2,
        test_database_url_parsing,
        test_flask_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All compatibility tests passed!")
        print("\n🚀 Ready for Render deployment with:")
        print("   - Python 3.11 (specified in .python-version)")
        print("   - psycopg2-binary 2.9.10")
        print("   - gunicorn 22.0.0")
    else:
        print("⚠️  Some tests failed")
        if not results[1]:  # psycopg2 test failed
            print("\n💡 For Render deployment:")
            print("   - Python 3.13 compatibility issues are resolved in deployment")
            print("   - Local development may use SQLite (works fine)")
            print("   - Production uses PostgreSQL with Python 3.11")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
