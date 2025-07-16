from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app import create_app
    
    # Create the Flask application
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    # For compatibility with different deployment platforms
    application = app
    
    print(f"✅ Flask app created successfully in {os.getenv('FLASK_ENV', 'production')} mode")
    
except Exception as e:
    print(f"❌ Error creating Flask app: {e}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")  # Show first 3 paths
    raise

if __name__ == "__main__":
    app.run()
