#!/usr/bin/env python3
"""
Test runner for YouTube Video Search Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def run_backend_tests():
    """Run backend tests"""
    print("🧪 Running Backend Tests...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Run pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_main.py", "-v", "--tb=short"
        ], capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All backend tests passed!")
            return True
        else:
            print("\n❌ Some backend tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 YouTube Video Search - Test Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Run backend tests
    backend_success = run_backend_tests()
    
    print("\n" + "=" * 50)
    if backend_success:
        print("🎉 All tests completed successfully!")
    else:
        print("💥 Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 