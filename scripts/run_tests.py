#!/usr/bin/env python3
"""
E-commerce API Test Runner

Runs all unit tests for the E-commerce API using pytest.
"""

import os
import sys
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_tests():
    """Run all tests using pytest"""
    print("🧪 E-commerce API Unit Tests")
    print("=" * 50)
    
    # Set up test environment
    os.environ['FLASK_ENV'] = 'testing'
    
    # Change to project root directory
    os.chdir(project_root)
    
    try:
        # Run pytest from the project root
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            '-v', 
            'tests/',
            '--tb=short'
        ], capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
