#!/usr/bin/env python3
"""
Dual Backend Server Runner
Runs both Flask and FastAPI servers for Stu-dih
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_flask_server():
    """Run Flask server on port 8000"""
    print("🚀 Starting Flask server on port 8000...")
    flask_script = Path("backend/flask_app.py")
    if flask_script.exists():
        return subprocess.Popen([sys.executable, str(flask_script)])
    else:
        print("⚠️  Flask app not found at backend/flask_app.py")
        return None

def run_fastapi_server():
    """Run FastAPI server on port 8001"""
    print("🚀 Starting FastAPI server on port 8001...")
    fastapi_script = Path("backend/main.py")
    if fastapi_script.exists():
        return subprocess.Popen([sys.executable, str(fastapi_script)])
    else:
        print("⚠️  FastAPI app not found at backend/main.py")
        return None

def main():
    print("🚀 Starting Stu-dih Dual Backend Servers...")
    print("📖 Flask API: http://localhost:8000")
    print("📖 FastAPI Documentation: http://localhost:8001/docs")
    print("🔗 Health Checks: http://localhost:8000/health, http://localhost:8001/health")
    print("⏹️  Press Ctrl+C to stop all servers")
    
    # Start Flask server
    flask_process = run_flask_server()
    
    # Start FastAPI server
    fastapi_process = run_fastapi_server()
    
    # Wait for processes to start
    time.sleep(3)
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if flask_process and flask_process.poll() is not None:
                print("⚠️  Flask server stopped unexpectedly")
                flask_process = None
                
            if fastapi_process and fastapi_process.poll() is not None:
                print("⚠️  FastAPI server stopped unexpectedly")
                fastapi_process = None
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate Flask server
        if flask_process:
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flask_process.kill()
            print("✅ Flask server stopped")
            
        # Terminate FastAPI server
        if fastapi_process:
            fastapi_process.terminate()
            try:
                fastapi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                fastapi_process.kill()
            print("✅ FastAPI server stopped")
            
        print("👋 All servers stopped")

if __name__ == "__main__":
    main() 