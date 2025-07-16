from app import create_app, db
from app.models import *

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
    app.run(debug=True, host='0.0.0.0', port=5000)
