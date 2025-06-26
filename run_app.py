#!/usr/bin/env python3
"""
Simple script to run and check the YouTube Video Search Application
"""

import subprocess
import time
import requests
import webbrowser
from pathlib import Path

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def check_frontend():
    """Check if frontend is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    print("🎬 YouTube Video Search Application")
    print("=" * 50)
    
    # Check if backend is running
    print("🔍 Checking backend status...")
    if check_backend():
        print("✅ Backend is running on http://localhost:8000")
    else:
        print("❌ Backend is not running")
        print("💡 To start backend: cd backend && python flask_app.py")
        return
    
    # Check if frontend is running
    print("🔍 Checking frontend status...")
    if check_frontend():
        print("✅ Frontend is running on http://localhost:3000")
    else:
        print("❌ Frontend is not running")
        print("💡 To start frontend: cd frontend && npm start")
        return
    
    print("\n🎉 Application is ready!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📖 API Health: http://localhost:8000/health")
    
    # Ask if user wants to open the app
    try:
        response = input("\n🌐 Open the application in your browser? (y/n): ")
        if response.lower() in ['y', 'yes']:
            webbrowser.open("http://localhost:3000")
            print("🚀 Opening application in browser...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n💡 To stop the application:")
    print("   - Press Ctrl+C in the backend terminal")
    print("   - Press Ctrl+C in the frontend terminal")

if __name__ == "__main__":
    main() 