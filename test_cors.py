#!/usr/bin/env python3
"""
CORS Test Script
Tests if the backend servers are properly configured for CORS
"""

import requests
import json

def test_cors_endpoint(url, origin):
    """Test CORS headers for a specific endpoint"""
    try:
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # Test preflight request
        response = requests.options(url, headers=headers)
        
        print(f"Testing {url} with origin {origin}")
        print(f"Status Code: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not found')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not found')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'Not found')}")
        print("-" * 50)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error testing {url}: {e}")
        return False

def main():
    print("🧪 Testing CORS Configuration")
    print("=" * 50)
    
    # Test Flask server (port 8000)
    print("Testing Flask Server (Port 8000):")
    flask_urls = [
        "http://localhost:8000/health",
        "http://localhost:8000/study/subjects"
    ]
    
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    flask_working = False
    for url in flask_urls:
        for origin in origins:
            if test_cors_endpoint(url, origin):
                flask_working = True
    
    print("\nTesting FastAPI Server (Port 8001):")
    fastapi_urls = [
        "http://localhost:8001/health",
        "http://localhost:8001/study/subjects"
    ]
    
    fastapi_working = False
    for url in fastapi_urls:
        for origin in origins:
            if test_cors_endpoint(url, origin):
                fastapi_working = True
    
    print("\n📊 Test Results:")
    print(f"Flask Server (8000): {'✅ Working' if flask_working else '❌ Not Working'}")
    print(f"FastAPI Server (8001): {'✅ Working' if fastapi_working else '❌ Not Working'}")
    
    if flask_working and fastapi_working:
        print("\n🎉 CORS is properly configured for both servers!")
    else:
        print("\n⚠️  Some servers may not be running or CORS is not properly configured.")
        print("Make sure to start the servers first:")
        print("  - Flask: python backend/flask_app.py")
        print("  - FastAPI: python backend/main.py")
        print("  - Both: python run_backend_dual.py")

if __name__ == "__main__":
    main() 