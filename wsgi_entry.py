import os
import sys

print("=" * 50)
print("WSGI Entry Point Starting")
print("=" * 50)

try:
    print("1. Importing create_app...")
    from app import create_app
    print("   ✓ Successfully imported create_app")
    
    print("2. Getting FLASK_ENV...")
    config = os.getenv('FLASK_ENV', 'production')
    print(f"   ✓ FLASK_ENV = {config}")
    
    print("3. Creating app...")
    app = create_app(config)
    print("   ✓ App created successfully")
    print("=" * 50)
    
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
