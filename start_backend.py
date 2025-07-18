#!/usr/bin/env python3
"""
Startup script for the YouTube Video Search Backend
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path for robust imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        import googleapiclient
        print("✓ All Python dependencies are installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy env.example to .env and add your YouTube API key")
        return False
    return True

def check_ytdlp():
    """Check if yt-dlp is available"""
    try:
        result = subprocess.run(["yt-dlp", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ yt-dlp is available (version: {result.stdout.strip()})")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  yt-dlp not found in PATH")
    print("The application will still work with YouTube API, but fallback may not work")
    return False

def main():
    """Main startup function"""
    print("🚀 Starting YouTube Video Search Backend...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_env_file()
    
    # Check yt-dlp
    check_ytdlp()
    
    print("\n" + "=" * 50)
    print("✅ Backend checks completed")
    print("\nStarting server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        
        # Try to import the app to check if study routes are available
        try:
            from backend.main import app
            print("✅ Backend app imported successfully")
            
            # Check if study routes are included
            study_routes_available = any(
                route.path.startswith("/study") 
                for route in app.routes 
                if hasattr(route, 'path')
            )
            
            if study_routes_available:
                print("✅ Study routes are available")
            else:
                print("⚠️  Study routes not found - check import logs above")
                
        except ImportError as e:
            print(f"⚠️  Warning importing backend: {e}")
            print("Continuing with server startup...")
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 