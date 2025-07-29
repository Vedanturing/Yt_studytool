#!/usr/bin/env python3
"""
Restart Flask Server
Stops the existing Flask server and starts the CORS-fixed version
"""

import subprocess
import sys
import time
import os
import signal
import psutil

def find_flask_processes():
    """Find Flask processes running on port 8000"""
    flask_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'flask' in cmdline.lower() and '8000' in cmdline:
                    flask_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return flask_processes

def kill_flask_processes():
    """Kill all Flask processes"""
    processes = find_flask_processes()
    if processes:
        print(f"🛑 Found {len(processes)} Flask process(es), stopping them...")
        for proc in processes:
            try:
                proc.terminate()
                print(f"   Terminated process {proc.pid}")
            except psutil.NoSuchProcess:
                pass
        
        # Wait a moment for processes to terminate
        time.sleep(2)
        
        # Force kill if still running
        for proc in processes:
            try:
                if proc.is_running():
                    proc.kill()
                    print(f"   Force killed process {proc.pid}")
            except psutil.NoSuchProcess:
                pass
    else:
        print("✅ No Flask processes found running on port 8000")

def start_cors_fixed_flask():
    """Start the CORS-fixed Flask server"""
    print("🚀 Starting CORS Fixed Flask Server...")
    try:
        subprocess.run([sys.executable, "backend/cors_fixed_flask_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 CORS Fixed Flask server stopped")
    except Exception as e:
        print(f"❌ Error starting CORS Fixed Flask server: {e}")

def main():
    print("🔄 Flask Server Restart")
    print("=" * 30)
    
    # Kill existing Flask processes
    kill_flask_processes()
    
    # Wait a moment
    time.sleep(1)
    
    # Start new CORS-fixed Flask server
    start_cors_fixed_flask()

if __name__ == "__main__":
    main() 