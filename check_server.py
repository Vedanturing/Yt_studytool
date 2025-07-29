#!/usr/bin/env python3
"""
Server Status Checker
Checks if the backend servers are running and tests CORS headers
"""

import requests
import time
import sys

def check_server(url, name):
    """Check if a server is running and return CORS headers"""
    try:
        print(f"🔍 Checking {name} at {url}...")
        
        # Test basic connectivity
        response = requests.get(url, timeout=5)
        print(f"✅ {name} is running (Status: {response.status_code})")
        
        # Check CORS headers
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_methods = response.headers.get('Access-Control-Allow-Methods')
        cors_headers = response.headers.get('Access-Control-Allow-Headers')
        
        print(f"   CORS Origin: {cors_origin}")
        print(f"   CORS Methods: {cors_methods}")
        print(f"   CORS Headers: {cors_headers}")
        
        return True, cors_origin
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is not running at {url}")
        return False, None
    except requests.exceptions.Timeout:
        print(f"⏰ {name} timeout at {url}")
        return False, None
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")
        return False, None

def test_cors_preflight(url, origin, name):
    """Test CORS preflight request"""
    try:
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(url, headers=headers, timeout=5)
        
        print(f"🧪 Testing CORS preflight for {name} with origin {origin}")
        print(f"   Status: {response.status_code}")
        print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not found')}")
        print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not found')}")
        print(f"   Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not found')}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ CORS preflight test failed for {name}: {e}")
        return False

def main():
    print("🔍 Backend Server Status Check")
    print("=" * 50)
    
    # Check Flask server
    flask_running, flask_cors = check_server("http://localhost:8000/health", "Flask Server")
    
    # Check FastAPI server
    fastapi_running, fastapi_cors = check_server("http://localhost:8001/health", "FastAPI Server")
    
    print("\n🧪 CORS Preflight Tests")
    print("=" * 30)
    
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    if flask_running:
        print("\nTesting Flask Server CORS:")
        for origin in origins:
            test_cors_preflight("http://localhost:8000/study/subjects", origin, "Flask")
    
    if fastapi_running:
        print("\nTesting FastAPI Server CORS:")
        for origin in origins:
            test_cors_preflight("http://localhost:8001/study/subjects", origin, "FastAPI")
    
    print("\n📊 Summary:")
    print(f"Flask Server (8000): {'✅ Running' if flask_running else '❌ Not Running'}")
    print(f"FastAPI Server (8001): {'✅ Running' if fastapi_running else '❌ Not Running'}")
    
    if not flask_running and not fastapi_running:
        print("\n⚠️  No backend servers are running!")
        print("Start the servers with:")
        print("  - Flask: python backend/flask_app.py")
        print("  - FastAPI: python backend/main.py")
        print("  - Both: python run_backend_dual.py")
    elif not flask_running:
        print("\n⚠️  Flask server is not running!")
        print("The frontend is trying to connect to port 8000 but Flask is not running.")
        print("Start Flask server: python backend/flask_app.py")
    else:
        print("\n✅ Flask server is running and should handle CORS requests")

if __name__ == "__main__":
    main() 