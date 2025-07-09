# E-commerce API Postman Collection Guide

## Overview

This guide explains how to use the comprehensive Postman collection for the E-commerce Backend API. The collection includes all endpoints, authentication flows, and admin features with automated token handling.

## Quick Setup

### 1. Import the Collection

1. Open Postman
2. Click "Import" button
3. Select the `E-commerce_API_Postman_Collection.json` file
4. The collection will be imported with all folders and requests

### 2. Set Environment Variables

The collection uses environment variables for easy testing. Set these in your Postman environment:

**Required Variables:**

- `base_url`: `http://localhost:5001` (or your server URL)

**Auto-managed Variables (set automatically by tests):**

- `access_token`: JWT access token
- `refresh_token`: JWT refresh token
- `user_id`: Current user ID
- `product_id`: Sample product ID
- `category_id`: Sample category ID
- `order_id`: Sample order ID
- `address_id`: Sample address ID

### 3. Environment Setup in Postman

1. Click the gear icon (⚙️) in the top right
2. Select "Manage Environments"
3. Click "Add" to create a new environment
4. Name it "E-commerce API Local"
5. Add the `base_url` variable with value `http://localhost:5001`
6. Save the environment
7. Select it from the dropdown in the top right

## Collection Structure

### 📁 Health & Info

- **Health Check**: `/ping` - Test if API is running
- **API Info**: `/api/v1` - Get API version and status

### 📁 Authentication

- **Register User**: Create new user account
- **Login User**: Login with admin/user credentials
- **Login Customer**: Login with customer credentials
- **Get Current User Profile**: Get authenticated user info
- **Refresh Token**: Refresh access token
- **Logout**: Logout current session
- **Update Profile**: Update user profile

### 📁 Products

- **Get All Products**: List all products
- **Get Products with Pagination**: Paginated product listing
- **Search Products**: Search products by name/description
- **Get Product by ID**: Get specific product details
- **Create Product (Admin)**: Add new product (admin only)
- **Update Product (Admin)**: Update product (admin only)
- **Delete Product (Admin)**: Remove product (admin only)

### 📁 Categories

- **Get All Categories**: List all categories
- **Get Category by ID**: Get specific category
- **Create Category (Admin)**: Add new category (admin only)
- **Update Category (Admin)**: Update category (admin only)
- **Delete Category (Admin)**: Remove category (admin only)

### 📁 Shopping Cart

- **Get Cart**: View current cart contents
- **Add Item to Cart**: Add product to cart
- **Update Cart Item**: Update item quantity
- **Remove Item from Cart**: Remove specific item
- **Clear Cart**: Empty entire cart
- **Apply Coupon**: Apply discount coupon

### 📁 Orders

- **Get User Orders**: List user's order history
- **Create Order from Cart**: Checkout cart as order
- **Get Order by ID**: Get specific order details
- **Cancel Order**: Cancel pending order
- **Track Order**: Get order tracking info

### 📁 User Management

- **Get User Addresses**: List user addresses
- **Add User Address**: Add new shipping address
- **Update User Address**: Update existing address
- **Delete User Address**: Remove address
- **Get Order History**: Get detailed order history
- **Get Activity Log**: Get user activity log

### 📁 Admin Dashboard

- **Get Dashboard Stats**: Admin dashboard statistics
- **Get All Users (Admin)**: List all users (admin only)
- **Get User Details (Admin)**: Get specific user details
- **Update User Status (Admin)**: Activate/deactivate users
- **Delete User (Admin)**: Remove user account
- **Get All Orders (Admin)**: List all orders
- **Update Order Status (Admin)**: Update order status
- **Get Activity Logs (Admin)**: System activity logs

### 📁 Shipping

- **Get Shipping Rates**: Calculate shipping costs
- **Create Shipment**: Create shipping label
- **Track Shipment**: Track shipping status
- **Update Shipment Status**: Update tracking info

## Testing Workflow

### 1. Authentication Flow

1. **Register User** or use existing credentials
2. **Login User** - This automatically sets `access_token` and `refresh_token`
3. All subsequent requests will use the stored tokens automatically

### 2. Basic E-commerce Flow

1. **Get All Products** - Browse available products
2. **Add Item to Cart** - Add products to cart
3. **Get Cart** - Review cart contents
4. **Create Order from Cart** - Checkout and create order
5. **Get Order by ID** - View order details

### 3. Admin Testing

1. **Login User** with admin credentials (email: admin@example.com, password: admin123)
2. **Get Dashboard Stats** - View admin dashboard
3. **Create Product** - Add new products
4. **Get All Users** - Manage users
5. **Update Order Status** - Process orders

## Auto-Token Management

The collection includes JavaScript test scripts that automatically:

- Extract JWT tokens from login responses
- Store tokens in environment variables
- Set user IDs and resource IDs for subsequent requests
- Handle token refresh automatically

## Sample Test Data

The API comes with sample data including:

- **Admin User**: admin@example.com / admin123
- **Customer User**: customer@example.com / customer123
- **Categories**: Electronics, Clothing, Books, Home & Garden
- **Products**: Various sample products with different categories
- **Sample addresses and orders**

## Error Handling

The collection handles common scenarios:

- Invalid credentials
- Missing authentication
- Resource not found
- Validation errors
- Server errors

## Tips for Testing

1. **Start with Health Check** to ensure API is running
2. **Login first** to set authentication tokens
3. **Use the provided sample data** for consistent testing
4. **Check response status codes** and messages
5. **Review auto-generated variables** after requests
6. **Use the Console** to debug any issues

## API Documentation

For detailed API documentation, refer to:

- `README.md` - Setup and deployment guide
- `API_EXAMPLES.md` - Detailed endpoint examples
- The Flask API itself provides JSON responses with clear structure

## Troubleshooting

**Common Issues:**

1. **401 Unauthorized**: Login first to get valid tokens
2. **403 Forbidden**: Check if user has required role (admin)
3. **404 Not Found**: Verify endpoint URLs and resource IDs
4. **500 Server Error**: Check server logs and ensure database is running

**Server Setup:**

```bash
# Ensure the API server is running
cd /Users/abdoanany/development/back_end/ecommerc_api
source venv/bin/activate
python app.py
```

The server should be running on `http://localhost:5001` by default.
