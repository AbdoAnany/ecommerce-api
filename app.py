import os
from app import create_app, db
from app.models import *

# Create the Flask application instance
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Category': Category,
        'Tag': Tag,
        'Cart': Cart,
        'CartItem': CartItem,
        'Order': Order,
        'OrderItem': OrderItem,
        'Address': Address,
        'Payment': Payment,
        'Review': Review,
        'Coupon': Coupon,
        'ActivityLog': ActivityLog,
        'ProductImage': ProductImage
    }

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Determine if we're in production or development
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Starting Flask application on 0.0.0.0:{port}")
    print(f"📊 Debug mode: {debug_mode}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run the application
    # Important: bind to 0.0.0.0 for Render deployment
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port
    )
