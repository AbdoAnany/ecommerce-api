# Password Reset Guide

This guide explains all the ways to reset user passwords in your e-commerce API system.

## 🎯 Quick Summary

You have multiple methods to reset passwords:

1. **Command Line Scripts** - Direct database access
2. **API Endpoints** - RESTful password management
3. **Emergency Reset** - When you're locked out

---

## 📋 Table of Contents

1. [Command Line Methods](#1-command-line-methods)
2. [API Endpoints](#2-api-endpoints)
3. [Emergency Reset](#3-emergency-reset)
4. [Testing Examples](#4-testing-examples)
5. [Security Notes](#5-security-notes)

---

## 1. Command Line Methods

### **Script Usage:**

```bash
python update_user_to_admin.py [command] [parameters]
```

### **Available Commands:**

#### Generate Secure Password

```bash
python update_user_to_admin.py generate_password
```

**Output:**

```
🔑 Generated secure password: vTcX4FcqL4Je
💡 Copy this password and use it with the reset commands
```

#### Reset Password by User ID

```bash
python update_user_to_admin.py reset_password_id <user_id> <new_password>
```

**Example:**

```bash
python update_user_to_admin.py reset_password_id 1 mynewpassword123
```

#### Reset Password by Email

```bash
python update_user_to_admin.py reset_password_email <email> <new_password>
```

**Example:**

```bash
python update_user_to_admin.py reset_password_email user@example.com newpass123
```

#### Reset Admin Password to Default

```bash
python update_user_to_admin.py reset_admin
```

**Output:**

```
✅ Admin password reset to default!
🔑 Email: admin@example.com
🔑 Password: admin123
⚠️  Please change this password after login!
```

#### List All Users (to find IDs)

```bash
python update_user_to_admin.py list
```

---

## 2. API Endpoints

### **🔗 Admin Password Management Endpoints**

#### Reset Any User's Password (Admin Only)

```http
POST /api/v1/admin/users/{user_id}/reset-password
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "new_password": "newpassword123"
}
```

**Example Request:**

```bash
curl -X POST https://your-api.com/api/v1/admin/users/2/reset-password \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "newpass123"}'
```

**Response:**

```json
{
  "message": "Password reset successfully for user customer",
  "user": {
    "id": 2,
    "email": "customer@example.com",
    "username": "customer"
  }
}
```

#### Change Your Own Admin Password

```http
POST /api/v1/admin/change-password
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "current_password": "admin123",
  "new_password": "mynewsecurepassword"
}
```

**Response:**

```json
{
  "message": "Password changed successfully",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin"
  }
}
```

#### Reset Another Admin's Password (Super Admin)

```http
POST /api/v1/admin/reset-admin-password
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "admin_email": "admin2@example.com",
  "new_password": "temppass123"
}
```

#### Generate Secure Password

```http
GET /api/v1/admin/generate-password
Authorization: Bearer <admin_jwt_token>
```

**Response:**

```json
{
  "message": "Secure password generated",
  "password": "K9mR2$nX8vQp",
  "length": 12,
  "note": "Use this password with password reset endpoints"
}
```

---

## 3. Emergency Reset

### **When You're Locked Out**

If you can't access the admin account, use the emergency reset:

#### Step 1: Ensure ALLOW_DB_INIT is Set

In Render dashboard, verify environment variable:

```
ALLOW_DB_INIT=true
```

#### Step 2: Emergency Admin Reset

```bash
curl -X POST https://your-api.com/setup/reset-admin-password \
  -H "Content-Type: application/json" \
  -d '{
    "admin_email": "admin@example.com",
    "new_password": "admin123"
  }'
```

**Response:**

```json
{
  "message": "Admin password reset successfully",
  "admin_email": "admin@example.com",
  "new_password": "admin123",
  "warning": "Change this password after login"
}
```

---

## 4. Testing Examples

### **Complete Password Reset Workflow:**

#### 1. List Users to Find IDs

```bash
python update_user_to_admin.py list
```

#### 2. Generate Secure Password

```bash
python update_user_to_admin.py generate_password
# Output: vTcX4FcqL4Je
```

#### 3. Reset User Password

```bash
python update_user_to_admin.py reset_password_id 2 vTcX4FcqL4Je
```

#### 4. Test Login with New Password

```bash
curl -X POST https://your-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "vTcX4FcqL4Je"
  }'
```

### **API Testing Workflow:**

#### 1. Login as Admin

```bash
curl -X POST https://your-api.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
# Save the access_token
```

#### 2. Generate Secure Password

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-api.com/api/v1/admin/generate-password
```

#### 3. Reset User Password

```bash
curl -X POST https://your-api.com/api/v1/admin/users/2/reset-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_password": "newpass123"}'
```

---

## 5. Security Notes

### **🔒 Security Best Practices:**

1. **Strong Passwords**: Always use generated secure passwords
2. **Change Defaults**: Change admin123 immediately after reset
3. **Token Security**: Admin tokens should have shorter expiration
4. **Emergency Access**: Remove ALLOW_DB_INIT after setup
5. **Audit Logging**: Log all password reset activities

### **🚨 Emergency Procedures:**

1. **Admin Locked Out**: Use emergency reset endpoint
2. **Forgotten Password**: Use command line reset
3. **Compromised Account**: Reset password immediately
4. **Multiple Admins**: Each admin can reset others' passwords

### **⚠️ Important Warnings:**

- Never share admin credentials
- Use HTTPS for all API calls
- Rotate passwords regularly
- Monitor failed login attempts
- Keep emergency access methods secure

---

## 📞 Quick Reference Commands

```bash
# List all users
python update_user_to_admin.py list

# Generate secure password
python update_user_to_admin.py generate_password

# Reset admin to default
python update_user_to_admin.py reset_admin

# Reset user by ID
python update_user_to_admin.py reset_password_id 1 newpass123

# Reset user by email
python update_user_to_admin.py reset_password_email user@example.com newpass123

# Emergency API reset (when ALLOW_DB_INIT=true)
curl -X POST https://your-api.com/setup/reset-admin-password \
  -H "Content-Type: application/json" \
  -d '{"new_password": "admin123"}'
```

---

## 🎉 Success!

You now have comprehensive password reset capabilities:

- ✅ Command line scripts for direct access
- ✅ RESTful API endpoints for admin management
- ✅ Emergency reset procedures for lockout situations
- ✅ Secure password generation
- ✅ Complete testing workflows

Your password management system is fully functional and secure!
