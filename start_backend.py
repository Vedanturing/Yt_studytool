#!/usr/bin/env python3
"""
Quick Backend Starter
Provides easy options to start different backend configurations
"""

import subprocess
import sys
import os
import time

def print_banner():
    print("🚀 Stu-dih Backend Quick Starter")
    print("=" * 40)

def print_options():
    print("\n📋 Available Options:")
    print("1. Simple Flask Server (Port 8000) - Recommended for CORS issues")
    print("2. Full Flask Server (Port 8000)")
    print("3. FastAPI Server (Port 8001)")
    print("4. Both Servers (Flask 8000 + FastAPI 8001)")
    print("5. Check server status")
    print("6. Exit")

def start_simple_flask():
    print("\n🚀 Starting Simple Flask Server...")
    print("This version has hardcoded CORS configuration for maximum compatibility.")
    
    try:
        subprocess.run([sys.executable, "backend/simple_flask_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Simple Flask server stopped")
    except Exception as e:
        print(f"❌ Error starting Simple Flask server: {e}")

def start_full_flask():
    print("\n🚀 Starting Full Flask Server...")
    
    try:
        subprocess.run([sys.executable, "backend/flask_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Full Flask server stopped")
    except Exception as e:
        print(f"❌ Error starting Full Flask server: {e}")

def start_fastapi():
    print("\n🚀 Starting FastAPI Server...")
    
    try:
        subprocess.run([sys.executable, "backend/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")

def start_both_servers():
    print("\n🚀 Starting Both Servers...")
    print("This will start Flask on port 8000 and FastAPI on port 8001")
    
    try:
        subprocess.run([sys.executable, "run_backend_dual.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Both servers stopped")
    except Exception as e:
        print(f"❌ Error starting both servers: {e}")

def check_server_status():
    print("\n🔍 Checking Server Status...")
    
    try:
        subprocess.run([sys.executable, "check_server.py"], check=True)
    except Exception as e:
        print(f"❌ Error checking server status: {e}")

def main():
    print_banner()
    
    while True:
        print_options()
        
        try:
            choice = input("\n👉 Enter your choice (1-6): ").strip()
            
            if choice == "1":
                start_simple_flask()
            elif choice == "2":
                start_full_flask()
            elif choice == "3":
                start_fastapi()
            elif choice == "4":
                start_both_servers()
            elif choice == "5":
                check_server_status()
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 