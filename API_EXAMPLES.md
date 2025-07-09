# E-commerce API - Quick Reference & Examples

## 🚀 Quick Start

```bash
# Setup (first time only)
./setup.sh

# Start development server
./run.sh
```

## 📡 API Examples

### Authentication

#### Register New User

```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### Login

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "customer123"
  }'
```

#### Get Current User Info

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Products

#### Get All Products

```bash
curl -X GET "http://localhost:5000/api/v1/products"
```

#### Get Products with Filters

```bash
curl -X GET "http://localhost:5000/api/v1/products?search=phone&category_id=1&min_price=100&max_price=1000&sort_by=price&sort_order=asc"
```

#### Get Featured Products

```bash
curl -X GET "http://localhost:5000/api/v1/products/featured?limit=5"
```

#### Search Products

```bash
curl -X GET "http://localhost:5000/api/v1/products/search?q=smartphone"
```

#### Create Product (Admin Only)

```bash
curl -X POST http://localhost:5000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -d '{
    "name": "New Smartphone",
    "description": "Latest smartphone with advanced features",
    "short_description": "Advanced smartphone",
    "sku": "PHONE-002",
    "price": 699.99,
    "stock_quantity": 25,
    "category_id": 1,
    "tags": ["new", "featured"],
    "is_featured": true
  }'
```

### Categories

#### Get All Categories

```bash
curl -X GET "http://localhost:5000/api/v1/categories"
```

#### Get Category Tree

```bash
curl -X GET "http://localhost:5000/api/v1/categories/tree"
```

#### Create Category (Admin Only)

```bash
curl -X POST http://localhost:5000/api/v1/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -d '{
    "name": "Smart Home",
    "description": "Smart home devices and accessories",
    "parent_id": 1
  }'
```

### Shopping Cart

#### Get Cart

```bash
curl -X GET http://localhost:5000/api/v1/cart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Add Item to Cart

```bash
curl -X POST http://localhost:5000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

#### Update Cart Item

```bash
curl -X PUT http://localhost:5000/api/v1/cart/update/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "quantity": 3
  }'
```

#### Remove Item from Cart

```bash
curl -X DELETE http://localhost:5000/api/v1/cart/remove/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Clear Cart

```bash
curl -X DELETE http://localhost:5000/api/v1/cart/clear \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Orders

#### Create Order

```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "shipping_address_id": 1,
    "billing_address_id": 1,
    "payment_method": "stripe",
    "notes": "Please deliver during business hours"
  }'
```

#### Get Order by Number

```bash
curl -X GET http://localhost:5000/api/v1/orders/ORD-ABC12345 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Process Payment

```bash
curl -X POST http://localhost:5000/api/v1/orders/1/payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "payment_method": "stripe"
  }'
```

### User Management

#### Get User Profile

```bash
curl -X GET http://localhost:5000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Profile

```bash
curl -X PUT http://localhost:5000/api/v1/users/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+1234567890"
  }'
```

#### Get User Orders

```bash
curl -X GET "http://localhost:5000/api/v1/users/orders?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get User Dashboard

```bash
curl -X GET http://localhost:5000/api/v1/users/dashboard \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Shipping & Addresses

#### Get User Addresses

```bash
curl -X GET http://localhost:5000/api/v1/shipping/addresses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Address

```bash
curl -X POST http://localhost:5000/api/v1/shipping/addresses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "type": "shipping",
    "first_name": "John",
    "last_name": "Doe",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US",
    "phone": "+1234567890",
    "is_default": true
  }'
```

#### Calculate Shipping

```bash
curl -X POST http://localhost:5000/api/v1/shipping/calculate-shipping \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "address_id": 1,
    "total_weight": 2.5,
    "total_value": 299.99
  }'
```

### Admin Dashboard

#### Get Dashboard Metrics (Admin Only)

```bash
curl -X GET http://localhost:5000/api/v1/admin/dashboard \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Get All Users (Admin Only)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/users?page=1&per_page=20" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Get All Orders (Admin Only)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/orders?status=pending&page=1" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Update Order Status (Admin Only)

```bash
curl -X PUT http://localhost:5000/api/v1/admin/orders/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -d '{
    "status": "shipped",
    "tracking_number": "TRK123456789"
  }'
```

#### Get Sales Analytics (Admin Only)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/analytics/sales?days=30" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 🔐 Authentication Tokens

After successful login, you'll receive an access token. Use it in subsequent requests:

```bash
# Save token from login response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use in requests
curl -X GET http://localhost:5000/api/v1/users/profile \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Response Examples

### Successful Response

```json
{
  "message": "Products retrieved successfully",
  "data": [
    {
      "id": 1,
      "name": "Smartphone Pro X",
      "price": 899.99,
      "stock_quantity": 50,
      "is_in_stock": true
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Response

```json
{
  "error": "Product not found"
}
```

## 🧪 Testing

Run the API test suite:

```bash
python test_api.py
```

## 📚 Documentation

- **Health Check**: `GET /ping`
- **API Info**: `GET /api/v1`
- **Full API Documentation**: Available in the code comments

## 🎯 Key Features Demonstrated

✅ **JWT Authentication** - Secure token-based auth
✅ **Role-based Access** - Admin/Customer permissions  
✅ **CRUD Operations** - Complete product management
✅ **Shopping Cart** - Persistent cart functionality
✅ **Order Processing** - Full order lifecycle
✅ **User Management** - Profile and order history
✅ **Admin Dashboard** - Analytics and management
✅ **Address Management** - Multiple shipping addresses
✅ **Search & Filtering** - Advanced product search
✅ **Pagination** - Efficient data loading
✅ **Input Validation** - Secure data handling
✅ **Error Handling** - Proper HTTP status codes

This is a production-ready e-commerce backend API with comprehensive features and clean architecture! 🚀
