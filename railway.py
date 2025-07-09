"""
Railway deployment configuration
"""
import os

# Railway automatically sets PORT
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    app.run(host="0.0.0.0", port=port)