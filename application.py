print("Starting application.py...")
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    app = create_app('production')
    print("✓ Successfully created app")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
