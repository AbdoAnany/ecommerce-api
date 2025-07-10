# Admin User Management Guide

This guide explains how to get/retrieve admin users in your e-commerce API system.

## 🎯 Quick Summary

Your system currently has **1 admin user**:

- **Email**: admin@example.com
- **Password**: admin123
- **Username**: admin
- **Status**: Active & Verified

## 📋 Table of Contents

1. [Database Query Methods](#database-query-methods)
2. [API Endpoints](#api-endpoints)
3. [Command Line Tools](#command-line-tools)
4. [Code Examples](#code-examples)
5. [Testing](#testing)

---

## 1. Database Query Methods

### Basic Retrieval

```python
from app.models import User, UserRole

# Get the first admin user
admin = User.query.filter_by(role=UserRole.ADMIN).first()

# Get all admin users
admins = User.query.filter_by(role=UserRole.ADMIN).all()

# Get admin by email
admin = User.query.filter_by(email='admin@example.com').first()

# Get active admin users only
active_admins = User.query.filter_by(role=UserRole.ADMIN, is_active=True).all()
```

### Advanced Queries

```python
# Search admin users
search_term = "admin"
admins = User.query.filter(
    User.role == UserRole.ADMIN,
    db.or_(
        User.email.contains(search_term),
        User.username.contains(search_term),
        User.first_name.contains(search_term),
        User.last_name.contains(search_term)
    )
).all()

# Get admin with recent login
recent_admin = User.query.filter(
    User.role == UserRole.ADMIN,
    User.last_login.isnot(None)
).order_by(User.last_login.desc()).first()
```

---

## 2. API Endpoints

### 🔗 New Admin User Endpoints

#### Get All Admin Users

```http
GET /api/v1/admin/admin-users
Authorization: Bearer <admin_jwt_token>
```

**Query Parameters:**

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20, max: 100)
- `is_active` - Filter by active status (true/false)
- `search` - Search by name, email, username

**Example Request:**

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     "https://your-api.com/api/v1/admin/admin-users?is_active=true&search=admin"
```

**Response:**

```json
{
  "message": "Admin users retrieved successfully",
  "data": [
    {
      "id": 1,
      "email": "admin@example.com",
      "username": "admin",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "role": "admin",
      "is_active": true,
      "is_verified": true,
      "created_at": "2024-01-01T00:00:00",
      "last_login": "2024-01-01T12:00:00",
      "orders_count": 0
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

#### Get Current Admin User

```http
GET /api/v1/admin/current-admin
Authorization: Bearer <admin_jwt_token>
```

**Response:**

```json
{
  "message": "Current admin user retrieved",
  "data": {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User",
    "role": "admin",
    "is_active": true,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00",
    "last_login": "2024-01-01T12:00:00"
  }
}
```

#### Get Admin Statistics

```http
GET /api/v1/admin/admin-stats
Authorization: Bearer <admin_jwt_token>
```

**Response:**

```json
{
  "message": "Admin statistics retrieved",
  "data": {
    "counts": {
      "total_admins": 1,
      "active_admins": 1,
      "verified_admins": 1
    },
    "recent_logins": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "last_login": "2024-01-01T12:00:00"
      }
    ]
  }
}
```

### 🔗 Existing Endpoints

#### Get All Users (Filter by Admin)

```http
GET /api/v1/admin/users?role=admin
Authorization: Bearer <admin_jwt_token>
```

---

## 3. Command Line Tools

### Check Admin Users Script

```bash
# Run the admin checker
python get_admin_users.py check

# Get specific admin by email
python get_admin_users.py get admin@example.com

# Create new admin user
python get_admin_users.py create admin2@example.com admin2 Admin Two admin123
```

### Output Example:

```
🔍 Checking Admin Users
==================================================
✅ Found 1 admin user(s):

👤 Admin User #1:
   ID: 1
   Email: admin@example.com
   Username: admin
   Name: Admin User
   Active: ✅
   Verified: ✅
   Created: 2025-07-09 21:51:27.280328
   Last Login: 2025-07-09 22:13:10.579923

📊 Admin Statistics:
   Total Admins: 1
   Active Admins: 1
   Verified Admins: 1

🔐 Login Information:
   Email: admin@example.com
   Password: admin123 (default)
   ⚠️  Change password after first login!
```

---

## 4. Code Examples

### Flask View Function

```python
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, UserRole

@app.route('/get-admin-users')
@jwt_required()
def get_admin_users():
    # Verify current user is admin
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'Admin access required'}), 403

    # Get all admin users
    admin_users = User.query.filter_by(role=UserRole.ADMIN).all()

    result = [
        {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.get_full_name(),
            'is_active': user.is_active,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        for user in admin_users
    ]

    return jsonify({
        'message': 'Admin users retrieved',
        'data': result,
        'count': len(result)
    })
```

### Utility Functions

```python
def get_main_admin():
    """Get the main admin user"""
    return User.query.filter_by(
        email='admin@example.com',
        role=UserRole.ADMIN
    ).first()

def check_if_admin_exists():
    """Check if any admin user exists"""
    return User.query.filter_by(role=UserRole.ADMIN).first() is not None

def get_admin_count():
    """Get total admin count"""
    return User.query.filter_by(role=UserRole.ADMIN).count()
```

---

## 5. Testing

### Test API Endpoints

1. **Login as admin first:**

```bash
curl -X POST https://your-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

2. **Use the access token to get admin users:**

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://your-api.com/api/v1/admin/admin-users
```

3. **Test admin statistics:**

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://your-api.com/api/v1/admin/admin-stats
```

### Test Database Queries

```python
# In Python shell or script
from app import create_app
from app.models import User, UserRole

app = create_app()
with app.app_context():
    # Test queries
    admin = User.query.filter_by(role=UserRole.ADMIN).first()
    print(f"Admin found: {admin.email if admin else 'None'}")

    all_admins = User.query.filter_by(role=UserRole.ADMIN).all()
    print(f"Total admins: {len(all_admins)}")
```

---

## 🔒 Security Notes

1. **Admin Access Control**: All admin endpoints require JWT authentication and admin role verification
2. **Password Security**: Change default admin password immediately after first login
3. **Token Management**: Admin tokens should have shorter expiration times
4. **Audit Logging**: Consider logging admin user access and modifications

---

## 📞 Support

If you need help:

1. **Check admin status**: Run `python get_admin_users.py check`
2. **API Issues**: Verify JWT token and admin role
3. **Database Issues**: Check database connection and table initialization
4. **Login Problems**: Verify credentials and user status

---

## 🎉 Success!

You now have multiple ways to retrieve admin users:

- ✅ Database queries
- ✅ API endpoints
- ✅ Command line tools
- ✅ Code examples

Your admin user is ready to use:

- **Email**: admin@example.com
- **Password**: admin123
- **API Access**: All admin endpoints available
