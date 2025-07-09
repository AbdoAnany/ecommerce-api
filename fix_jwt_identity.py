#!/usr/bin/env python3
"""Script to fix get_jwt_identity() calls to convert to int"""

import os
import re

def fix_jwt_identity_file(filepath):
    """Fix get_jwt_identity() calls in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern to match user_id = get_jwt_identity()
    pattern = r'(\s+)user_id = get_jwt_identity\(\)'
    replacement = r'\1user_id = int(get_jwt_identity())'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    # Files to fix
    files_to_fix = [
        'app/users/routes.py',
        'app/cart/routes.py', 
        'app/orders/routes.py',
        'app/admin/routes.py',
        'app/shipping/routes.py'
    ]
    
    base_dir = '/Users/abdoanany/development/back_end/ecommerc_api'
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            fix_jwt_identity_file(full_path)
        else:
            print(f"File not found: {full_path}")

if __name__ == '__main__':
    main()
