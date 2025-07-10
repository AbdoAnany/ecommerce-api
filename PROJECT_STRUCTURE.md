# E-commerce API - Clean Project Structure

## 📁 Project Organization

```
ecommerc_api/
├── app/                          # Main application package
│   ├── __init__.py              # App factory
│   ├── models.py                # Database models
│   ├── setup.py                 # Setup utilities
│   ├── admin/                   # Admin functionality
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/                    # Authentication
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── categories/              # Category management
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── products/                # Product management
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── cart/                    # Shopping cart
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── orders/                  # Order management
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── users/                   # User management
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   └── shipping/                # Shipping functionality
│       ├── __init__.py
│       └── routes.py
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── base.py                  # Test base classes
│   ├── test_auth.py
│   ├── test_admin.py
│   ├── test_categories.py
│   ├── test_products.py
│   └── test_setup.py
├── scripts/                     # Utility scripts
│   ├── init_db.py              # Database initialization
│   ├── create_sample_data.py   # Sample data creation
│   └── run_tests.py            # Test runner
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific files
├── docs/                        # Documentation
│   ├── README.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── API_EXAMPLES.md
│   └── POSTMAN_GUIDE.md
├── config.py                    # Configuration
├── app.py                       # Application entry point
├── wsgi.py                      # WSGI configuration
├── requirements.txt             # Dependencies
├── deploy.sh                    # Deployment script
├── test_all_endpoints.py        # Endpoint testing
└── .env.example                 # Environment variables template
```

## 🚀 Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize database:**

   ```bash
   flask db upgrade
   python scripts/create_sample_data.py
   ```

4. **Run the application:**

   ```bash
   python app.py
   ```

5. **Run tests:**
   ```bash
   python scripts/run_tests.py
   ```

## 📋 Key Features

- ✅ Multi-language support (English/Arabic)
- ✅ Advanced product management
- ✅ Category hierarchy
- ✅ User authentication & authorization
- ✅ Admin dashboard
- ✅ Shopping cart functionality
- ✅ Order management
- ✅ Comprehensive API testing
- ✅ Database migrations
- ✅ Production-ready deployment
