# E-commerce API Backend

A comprehensive, scalable e-commerce backend API built with Flask, SQLAlchemy, and JWT authentication.

## 🌐 Live Demo & Deployment

**Ready to deploy in 5 minutes!** Choose your preferred platform:

| Platform | Deployment | Database | Cost |
|----------|------------|----------|------|
| 🚂 **[Railway](https://railway.app)** | `./deploy_railway.sh` | PostgreSQL | Free tier |
| 🌟 **[Heroku](https://heroku.com)** | `./deploy_heroku.sh` | PostgreSQL | Free tier |
| 🎨 **[Render](https://render.com)** | One-click deploy | PostgreSQL | Free tier |
| 🐍 **[PythonAnywhere](https://pythonanywhere.com)** | Manual setup | MySQL | Free tier |

**📖 [See Full Deployment Guide](DEPLOYMENT_GUIDE.md)**

## 🚀 Features

### Core Functionality

- **JWT Authentication & Authorization** - Secure token-based authentication with role-based access control
- **User Management** - Registration, login, profile management, and order history
- **Product Management** - CRUD operations with search, filtering, and inventory management
- **Category System** - Hierarchical categories with tags support
- **Shopping Cart** - Persistent cart with real-time calculations
- **Order Management** - Complete order lifecycle from cart to delivery
- **Address Management** - Multiple shipping addresses per user
- **Admin Dashboard** - Comprehensive analytics and management tools

### Advanced Features

- **Payment Integration Ready** - Placeholder for Stripe/PayPal integration
- **Stock Management** - Automatic stock updates and low-stock alerts
- **Product Reviews & Ratings** - Customer feedback system
- **Coupon System** - Discount codes and promotions
- **Activity Logging** - Audit trail for user actions
- **File Upload Support** - Product image management
- **Guest Checkout** - Orders without registration

## 🛠 Tech Stack

- **Backend**: Flask 3.0+
- **Database**: SQLite (dev) / MySQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Migrations**: Flask-Migrate
- **CORS**: Flask-CORS
- **Password Hashing**: bcrypt

## 📁 Project Structure

```
ecommerce_api/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── auth/                # Authentication routes
│   ├── users/               # User management
│   ├── products/            # Product operations
│   ├── categories/          # Category management
│   ├── cart/                # Shopping cart
│   ├── orders/              # Order processing
│   ├── admin/               # Admin dashboard
│   └── shipping/            # Address management
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── app.py                   # Development server
├── wsgi.py                  # Production WSGI
├── deploy.py                # Deployment script
└── create_sample_data.py    # Sample data generator
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or create project directory
cd ecommerce_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Initialize Database

```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create sample data (optional)
python create_sample_data.py
```

### 4. Run Development Server

```bash
# Start development server
python app.py

# Or use Flask CLI
flask run
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info

### Products

- `GET /api/v1/products` - List products with filters
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/slug/{slug}` - Get product by slug
- `GET /api/v1/products/featured` - Get featured products
- `GET /api/v1/products/search` - Search products
- `POST /api/v1/products` - Create product (Admin)
- `PUT /api/v1/products/{id}` - Update product (Admin)
- `DELETE /api/v1/products/{id}` - Delete product (Admin)

### Categories

- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{id}` - Get category by ID
- `GET /api/v1/categories/tree` - Get hierarchical category tree
- `POST /api/v1/categories` - Create category (Admin)
- `PUT /api/v1/categories/{id}` - Update category (Admin)

### Cart

- `GET /api/v1/cart` - Get user's cart
- `POST /api/v1/cart/add` - Add item to cart
- `PUT /api/v1/cart/update/{item_id}` - Update cart item
- `DELETE /api/v1/cart/remove/{item_id}` - Remove cart item
- `DELETE /api/v1/cart/clear` - Clear cart

### Orders

- `POST /api/v1/orders` - Create order from cart
- `GET /api/v1/orders/{order_number}` - Get order by number
- `POST /api/v1/orders/{id}/payment` - Process payment
- `POST /api/v1/orders/{id}/cancel` - Cancel order

### User Management

- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `GET /api/v1/users/orders` - Get user's orders
- `GET /api/v1/users/dashboard` - Get user dashboard

### Admin

- `GET /api/v1/admin/dashboard` - Admin dashboard metrics
- `GET /api/v1/admin/users` - Manage users
- `GET /api/v1/admin/orders` - Manage orders
- `PUT /api/v1/admin/orders/{id}` - Update order status
- `GET /api/v1/admin/analytics/sales` - Sales analytics

### Shipping

- `GET /api/v1/shipping/addresses` - Get user addresses
- `POST /api/v1/shipping/addresses` - Create address
- `PUT /api/v1/shipping/addresses/{id}` - Update address
- `DELETE /api/v1/shipping/addresses/{id}` - Delete address

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Sample Login Request

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "customer123"
  }'
```

## 🏗 Database Models

### Core Models

- **User** - User accounts with role-based access
- **Product** - Product catalog with inventory
- **Category** - Hierarchical product categories
- **Order** - Order management with status tracking
- **Cart** - Shopping cart functionality
- **Address** - Shipping and billing addresses
- **Payment** - Payment transaction records

### Relationships

- Users have multiple Orders and Addresses
- Products belong to Categories and have Tags
- Orders contain OrderItems (product snapshots)
- Cart contains CartItems (current selections)

## 🔧 Configuration

### Environment Variables

```bash
# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite:///ecommerce.db

# JWT Settings
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Upload Settings
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## 🚀 Deployment

### PythonAnywhere Deployment

1. **Upload files** to your PythonAnywhere account
2. **Install dependencies** in a virtual environment
3. **Configure environment variables** in the Web tab
4. **Set up MySQL database** (production)
5. **Configure WSGI file** to point to `wsgi.py`

### Production Configuration

```python
# Update config.py for production
DATABASE_URL=mysql+pymysql://username:password@hostname/database_name
FLASK_ENV=production
DEBUG=False
```

## 🧪 Testing

### Sample Data

```bash
# Create test data
python create_sample_data.py
```

### Test Users

- **Admin**: admin@example.com / admin123
- **Customer**: customer@example.com / customer123

### API Testing

```bash
# Health check
curl http://localhost:5000/ping

# Get products
curl http://localhost:5000/api/v1/products

# Get API info
curl http://localhost:5000/api/v1
```

## 📚 API Documentation

### Response Format

All API responses follow this format:

```json
{
  "message": "Success message",
  "data": {}, // Response data
  "pagination": {} // For paginated responses
}
```

### Error Responses

```json
{
  "error": "Error message",
  "details": {} // Additional error details
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## 🔒 Security Features

- **Password Hashing** - bcrypt for secure password storage
- **JWT Tokens** - Secure authentication with expiration
- **Role-based Access** - Admin/Customer/Vendor roles
- **Input Validation** - Marshmallow schema validation
- **SQL Injection Protection** - SQLAlchemy ORM
- **CORS Support** - Cross-origin request handling
- **Token Blacklisting** - Logout token invalidation

## 📈 Performance Features

- **Database Indexing** - Optimized queries
- **Pagination** - Efficient data loading
- **Lazy Loading** - Optimized relationships
- **Caching Ready** - Prepared for Redis integration
- **Background Tasks Ready** - Celery integration ready

## 🎯 Future Enhancements

- **Email Integration** - Verification and notifications
- **Payment Gateways** - Stripe, PayPal integration
- **File Upload** - Product image management
- **Search Engine** - Elasticsearch integration
- **Caching Layer** - Redis for performance
- **Background Tasks** - Celery for async processing
- **API Documentation** - Swagger/OpenAPI
- **Testing Suite** - Unit and integration tests

## 📞 Support

This is a production-ready e-commerce API backend with comprehensive features and clean architecture. The codebase follows Flask best practices and is designed for scalability and maintainability.

For questions or customizations, refer to the inline code documentation and Flask official documentation.
