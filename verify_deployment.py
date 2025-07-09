#!/usr/bin/env python3
"""
Deployment verification script
Tests that all required components are working before deployment
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import wsgi
        print("✅ WSGI module imported successfully")
        
        if hasattr(wsgi, 'app'):
            print("✅ WSGI has 'app' object (required for Gunicorn)")
        else:
            print("❌ WSGI missing 'app' object")
            return False
            
        if hasattr(wsgi, 'application'):
            print("✅ WSGI has 'application' object (backward compatibility)")
        else:
            print("⚠️  WSGI missing 'application' object (not critical)")
            
    except ImportError as e:
        print(f"❌ WSGI import failed: {e}")
        return False
    
    try:
        from app import create_app
        app = create_app('production')
        print("✅ Flask app created successfully")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/ping')
            if response.status_code == 200:
                print("✅ Health check endpoint working")
            else:
                print(f"⚠️  Health check returned status {response.status_code}")
                
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False
    
    return True

def test_requirements():
    """Test that requirements.txt exists and is valid"""
    print("\n📦 Testing requirements...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().strip().split('\n')
        
    if len(requirements) > 0:
        print(f"✅ Requirements file has {len(requirements)} dependencies")
        
        # Check for essential packages
        req_text = '\n'.join(requirements).lower()
        essential = ['flask', 'gunicorn', 'sqlalchemy']
        
        for pkg in essential:
            if pkg in req_text:
                print(f"✅ {pkg} found in requirements")
            else:
                print(f"❌ {pkg} missing from requirements")
                return False
    else:
        print("❌ Requirements file is empty")
        return False
    
    return True

def test_config_files():
    """Test that configuration files exist"""
    print("\n⚙️  Testing configuration files...")
    
    config_files = {
        'wsgi.py': 'WSGI entry point',
        'Procfile': 'Heroku configuration',
        'render.yaml': 'Render configuration',
        'config.py': 'Flask configuration',
        'requirements.txt': 'Python dependencies'
    }
    
    all_good = True
    for file, description in config_files.items():
        if os.path.exists(file):
            print(f"✅ {file} ({description})")
        else:
            print(f"❌ {file} missing ({description})")
            all_good = False
    
    return all_good

def test_environment():
    """Test environment configuration"""
    print("\n🌍 Testing environment...")
    
    # Check if .env.example exists (good practice)
    if os.path.exists('.env.example'):
        print("✅ .env.example found (good practice)")
    else:
        print("⚠️  .env.example not found (recommended)")
    
    # Check if .env is in .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
        if '.env' in gitignore:
            print("✅ .env in .gitignore (security)")
        else:
            print("⚠️  .env not in .gitignore (potential security risk)")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Deployment Verification Script")
    print("=" * 40)
    
    tests = [
        test_requirements,
        test_config_files,
        test_imports,
        test_environment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment!")
        print("\n🚀 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Deploy to your chosen platform")
        print("3. Set environment variables")
        print("4. Test your deployed API")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
