# How to Update User to Admin Role

This guide shows you multiple ways to promote a user to admin role in your e-commerce API.

## 🎯 **Current Database Status**

You have **3 users** in your database:
- **ID 1**: admin@example.com (Already admin)
- **ID 2**: customer@example.com (Customer) 
- **ID 3**: test@example.com (Now admin)

---

## 🛠️ **Method 1: Command Line Script (Recommended)**

### **List All Users:**
```bash
python update_user_to_admin.py list
```

### **Update User by ID:**
```bash
# Update user ID 2 to admin
python update_user_to_admin.py update_id 2
```

### **Update User by Email:**
```bash
# Update user by email
python update_user_to_admin.py update_email customer@example.com
```

### **Example Output:**
```
📋 Current user details:
   ID: 2
   Email: customer@example.com
   Username: customer
   Name: John Doe
   Current Role: customer
   Active: True

✅ User customer (ID: 2) updated to admin successfully!
📧 Email: customer@example.com
👤 Role: admin
✔️  Active: True
✔️  Verified: True
```

---

## 🌐 **Method 2: API Endpoints (After Login)**

### **Step 1: Login as Admin**
```bash
curl -X POST https://your-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

### **Step 2: Promote User via API**
```bash
# Promote user ID 2 to admin
curl -X PUT https://your-api.com/api/v1/admin/promote-user/2 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "message": "User promoted to admin successfully",
  "data": {
    "id": 2,
    "email": "customer@example.com",
    "username": "customer",
    "full_name": "John Doe",
    "previous_role": "customer",
    "new_role": "admin",
    "is_active": true,
    "is_verified": true,
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

### **Bulk Promotion (Multiple Users):**
```bash
curl -X POST https://your-api.com/api/v1/admin/bulk-promote \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [2, 3]
  }'
```

---

## 🔧 **Method 3: Setup Endpoints (No Login Required)**

### **List Users:**
```bash
curl https://your-api.com/setup/list-users
```

### **Promote User:**
```bash
# By user ID
curl -X POST https://your-api.com/setup/promote-user \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'

# By email
curl -X POST https://your-api.com/setup/promote-user \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com"
  }'
```

**Response:**
```json
{
  "message": "User promoted to admin successfully",
  "user": {
    "id": 2,
    "email": "customer@example.com",
    "username": "customer",
    "full_name": "John Doe",
    "previous_role": "customer",
    "new_role": "admin",
    "is_active": true,
    "is_verified": true
  }
}
```

---

## 💻 **Method 4: Direct Database Query (Python)**

```python
from app import create_app
from app.models import User, UserRole
from app import db

app = create_app()
with app.app_context():
    # Update user ID 2 to admin
    user = User.query.get(2)
    if user:
        user.role = UserRole.ADMIN
        user.is_active = True
        user.is_verified = True
        db.session.commit()
        print(f"User {user.username} is now admin!")
```

---

## 🎯 **Test Your New Admin**

### **Test Login:**
```bash
curl -X POST https://your-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "customer123"
  }'
```

### **Test Admin Access:**
```bash
curl -H "Authorization: Bearer NEW_ADMIN_TOKEN" \
     https://your-api.com/api/v1/admin/dashboard
```

---

## ⚠️ **Important Notes**

1. **Security**: Only current admins can promote other users via API
2. **Setup Endpoints**: Only work when `ALLOW_DB_INIT=true`
3. **Auto-Activation**: Promoted users are automatically activated and verified
4. **Multiple Admins**: You can have multiple admin users
5. **Demotion**: Use `/api/v1/admin/demote-admin/{user_id}` to demote admins

---

## 🔄 **Demote Admin to User**

### **API Method:**
```bash
curl -X PUT https://your-api.com/api/v1/admin/demote-admin/3 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Command Line:**
```python
# Create demote script if needed
user = User.query.get(3)
user.role = UserRole.CUSTOMER
db.session.commit()
```

---

## 📊 **Summary**

- ✅ **Command Line**: `python update_user_to_admin.py update_id 2`
- ✅ **API Endpoint**: `PUT /api/v1/admin/promote-user/2`
- ✅ **Setup Endpoint**: `POST /setup/promote-user`
- ✅ **Direct Database**: Update `user.role = UserRole.ADMIN`

Choose the method that works best for your situation!
