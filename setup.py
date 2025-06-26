#!/usr/bin/env python3
"""
Setup script for YouTube Video Search Application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🎬 YouTube Video Search Application Setup")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def setup_env_file():
    """Setup environment file"""
    print("\n🔧 Setting up environment file...")
    
    env_example = Path("env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping...")
        return True
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and add your YouTube API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_node_installation():
    """Check if Node.js is installed"""
    print("\n🔍 Checking Node.js installation...")
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} is installed")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Node.js is not installed or not in PATH")
    print("Please install Node.js from https://nodejs.org/")
    return False

def install_frontend_dependencies():
    """Install frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        os.chdir(frontend_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        os.chdir("..")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your YouTube API key")
    print("2. Start the backend: python start_backend.py")
    print("3. Start the frontend: cd frontend && npm start")
    print("4. Open http://localhost:3000 in your browser")
    print("\n📚 For more information, see README.md")
    print("=" * 50)

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Setup environment file
    if not setup_env_file():
        sys.exit(1)
    
    # Check Node.js
    if not check_node_installation():
        print("\n⚠️  Frontend setup skipped due to missing Node.js")
        print_next_steps()
        return
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("\n⚠️  Frontend setup failed, but backend is ready")
        print_next_steps()
        return
    
    # All good
    print_next_steps()

if __name__ == "__main__":
    main() 