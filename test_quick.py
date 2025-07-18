#!/usr/bin/env python3
"""
Quick test to verify backend functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_study_subjects():
    """Test study subjects endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/study/subjects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            subjects = data.get('subjects', [])
            print(f"✅ Study subjects loaded: {len(subjects)} subjects")
            for subject in subjects:
                print(f"   - {subject['code']}: {subject['name']}")
            return True
        else:
            print(f"❌ Study subjects failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Study subjects error: {e}")
        return False

def test_study_units():
    """Test study units endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/study/subjects/315319-OPERATING SYSTEM/units", timeout=10)
        if response.status_code == 200:
            data = response.json()
            units = data.get('units', [])
            print(f"✅ Study units loaded: {len(units)} units")
            return True
        else:
            print(f"❌ Study units failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Study units error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Backend Test")
    print("=" * 30)
    
    # Test 1: Health check
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it with:")
        print("   python start_backend.py")
        exit(1)
    
    # Test 2: Study subjects
    if not test_study_subjects():
        print("\n❌ Study subjects endpoint failed")
        exit(1)
    
    # Test 3: Study units
    if not test_study_units():
        print("\n❌ Study units endpoint failed")
        exit(1)
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    print("\nYou can now:")
    print("1. Start the frontend: cd frontend && npm start")
    print("2. Navigate to http://localhost:3000")
    print("3. Click on the 'Study' tab to use the study module") 