# Updated E-commerce API Postman Collection Guide

This guide explains how to use the updated Postman collection with all the new admin management and password reset features.

## 🚀 **What's New in This Update**

### **New Sections Added:**
1. **Admin User Management** (in Admin Dashboard)
2. **Setup & Emergency** - Database setup and emergency access
3. **Testing & Utilities** - Quick testing endpoints

### **New Endpoints:**
- Get Admin Users
- Promote/Demote Users
- Password Reset Features
- Emergency Admin Reset
- Database Health & Setup

---

## 📋 **Collection Structure**

### **1. Health & Info**
- Health Check
- API Info

### **2. Authentication**
- Register User
- Login User/Admin/Customer
- Profile Management
- Token Refresh

### **3. Products**
- CRUD Operations
- Search & Filtering
- Admin Product Management

### **4. Categories**
- Category Management
- Hierarchical Categories

### **5. Shopping Cart**
- Cart Operations
- Coupon Application

### **6. Orders**
- Order Processing
- Order Tracking
- Order Management

### **7. User Management**
- Address Management
- Order History
- Activity Logs

### **8. Admin Dashboard** (Updated!)
- Dashboard Statistics
- User Management
- **🆕 Get Admin Users**
- **🆕 Promote User to Admin**
- **🆕 Demote Admin to User**
- **🆕 Bulk Promote Users**
- **🆕 Reset User Password**
- **🆕 Reset Admin Password**
- **🆕 Change Own Password**
- **🆕 Generate Secure Password**
- Order Management
- Analytics

### **9. Product Reviews**
- Review Management

### **10. Shipping**
- Shipping Methods
- Cost Calculation
- Tracking

### **11. Setup & Emergency** (New!)
- **🆕 Database Health Check**
- **🆕 Initialize Database**
- **🆕 List All Users**
- **🆕 Promote User (No Auth)**
- **🆕 Emergency Password Reset**

### **12. Testing & Utilities** (New!)
- **🆕 Test Admin Login**
- **🆕 Test Customer Login**
- **🆕 Quick System Status**
- **🆕 Quick Product Test**

---

## 🔧 **Setup Instructions**

### **Step 1: Import Collection**
1. Download the `E-commerce_API_Postman_Collection.json` file
2. Open Postman
3. Click **Import** → **Upload Files** → Select the JSON file
4. Collection will be imported with all endpoints

### **Step 2: Configure Environment**
The collection includes these variables:
- `base_url`: https://ecommerce-api-2owr.onrender.com (Production)
- `local_url`: http://localhost:5001 (Development)
- `admin_token`: Admin access token
- `customer_token`: Customer access token
- `access_token`: General access token

### **Step 3: Test Setup**
1. Run **"Quick System Status"** to verify API is running
2. Run **"Test Admin Login"** to get admin access
3. Run **"Get Dashboard Stats"** to verify admin access works

---

## 🎯 **Quick Start Workflows**

### **Admin Setup Workflow:**
```
1. Test Admin Login → Gets admin_token
2. Get Current Admin → Verify admin identity
3. Get Admin Users → See all admin users
4. Get Dashboard Stats → Verify admin access
```

### **User Management Workflow:**
```
1. Test Admin Login → Get admin access
2. Get All Users (Admin) → See all users
3. Promote User to Admin → Make user admin
4. Reset User Password → Change user password
5. Get Admin Users → Verify promotion worked
```

### **Emergency Access Workflow:**
```
1. Database Health Check → Verify system status
2. Emergency Admin Password Reset → Reset if locked out
3. Test Admin Login → Login with reset password
4. Change Own Password → Set new secure password
```

### **Product Testing Workflow:**
```
1. List Products (Quick Test) → Verify API works
2. Test Admin Login → Get admin access
3. Create Product → Test product creation
4. Get Product by ID → Verify product exists
```

---

## 🔐 **Authentication Patterns**

### **Multiple Token Management:**
The collection now supports different token types:

```javascript
// For Admin Operations
Authorization: Bearer {{admin_token}}

// For Customer Operations  
Authorization: Bearer {{customer_token}}

// For General Operations
Authorization: Bearer {{access_token}}
```

### **Auto Token Storage:**
Login endpoints automatically save tokens:
- **Test Admin Login** → Saves to `admin_token`
- **Test Customer Login** → Saves to `customer_token`
- **Login User** → Saves to `access_token`

---

## 📊 **New Admin Management Features**

### **🔍 Admin User Discovery:**
```http
GET /api/v1/admin/admin-users
- Filter by active status
- Search by name/email
- Pagination support
```

### **👥 User Role Management:**
```http
PUT /api/v1/admin/promote-user/{id}    # Promote to admin
PUT /api/v1/admin/demote-admin/{id}    # Demote to customer
POST /api/v1/admin/bulk-promote        # Promote multiple users
```

### **🔑 Password Management:**
```http
POST /api/v1/admin/users/{id}/reset-password  # Reset any user's password
POST /api/v1/admin/change-password            # Change own password
POST /api/v1/admin/reset-admin-password       # Reset another admin's password
GET /api/v1/admin/generate-password           # Generate secure password
```

### **🚨 Emergency Features:**
```http
POST /setup/reset-admin-password     # Emergency admin reset (no auth)
POST /setup/promote-user             # Emergency user promotion (no auth)
GET /setup/list-users                # List users (no auth)
```

---

## 🧪 **Testing Examples**

### **Test Admin Functions:**
1. **Run "Test Admin Login"**
   - Expected: 200 OK, admin_token saved
   
2. **Run "Get Admin Users"**
   - Expected: List of admin users
   
3. **Run "Generate Secure Password"**
   - Expected: Secure password returned
   
4. **Run "Promote User to Admin"** (use user_id: 2)
   - Expected: User promoted successfully

### **Test Emergency Features:**
1. **Run "Emergency Admin Password Reset"**
   - Expected: Admin password reset to admin123
   
2. **Run "List All Users (Setup)"**
   - Expected: All users listed (no auth required)

### **Test Password Reset:**
1. **Get admin access with "Test Admin Login"**
2. **Run "Reset User Password"** with new password
3. **Try logging in with new password**

---

## 🔒 **Security Notes**

### **Environment Variables:**
- Production URL: `https://ecommerce-api-2owr.onrender.com`
- Never commit tokens to version control
- Use separate tokens for different user types

### **Emergency Endpoints:**
- Only work when `ALLOW_DB_INIT=true`
- Should be disabled in production after setup
- Use only for emergency access

### **Password Security:**
- Always use generated secure passwords
- Change default passwords immediately
- Use strong authentication tokens

---

## 📞 **Troubleshooting**

### **Common Issues:**

#### **401 Unauthorized:**
- Solution: Run login endpoint to get fresh token
- Check if token is properly set in Authorization header

#### **403 Forbidden:**
- Solution: Use admin_token for admin endpoints
- Verify user has admin role

#### **Emergency Access Needed:**
- Use Setup & Emergency endpoints
- Verify ALLOW_DB_INIT=true in environment

#### **Database Connection Issues:**
- Run "Database Health Check"
- Check if database is initialized

---

## 🎉 **Complete Feature Set**

Your updated Postman collection now includes:

✅ **Complete API Testing** - All endpoints covered
✅ **Multi-Role Authentication** - Admin, Customer, General tokens
✅ **Admin User Management** - Promote, demote, list admin users
✅ **Password Management** - Reset, change, generate passwords
✅ **Emergency Access** - Setup and emergency endpoints
✅ **Automated Token Handling** - Auto-save and reuse tokens
✅ **Production Ready** - Production URLs configured
✅ **Testing Utilities** - Quick test endpoints
✅ **Comprehensive Documentation** - Built-in descriptions

The collection is now complete and ready for full-scale API testing and development! 🚀
