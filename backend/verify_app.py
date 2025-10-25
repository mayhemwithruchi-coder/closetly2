"""
Simple verification script to check if the app can be imported without errors
"""
try:
    # Try to import the Flask app
    from app import app
    print("✅ app.py imports successfully")
    
    # Try to import other modules
    import os
    print("✅ os module imports successfully")
    
    # Check if required files exist
    required_files = [
        'app.py',
        'closetly_india_complete.html',
        'price_api_integration.js',
        'requirements.txt',
        'render.yaml',
        'runtime.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    else:
        print("✅ All required files are present")
    
    # Check if the Flask app has the expected routes
    expected_routes = ['/', '/health', '/predict', '/compare', '/batch_predict']
    registered_routes = [rule.rule for rule in app.url_map.iter_rules()]
    
    missing_routes = []
    for route in expected_routes:
        if route not in registered_routes:
            missing_routes.append(route)
    
    if missing_routes:
        print(f"❌ Missing routes: {missing_routes}")
    else:
        print("✅ All expected routes are registered")
    
    print("🎉 App verification completed successfully!")
    
except Exception as e:
    print(f"❌ Error during verification: {e}")
    import traceback
    traceback.print_exc()