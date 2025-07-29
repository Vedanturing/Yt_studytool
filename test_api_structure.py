#!/usr/bin/env python3
"""
Test API Structure
Verifies that the API returns data in the format expected by the frontend
"""

import requests
import json

def test_subjects_endpoint():
    """Test the /study/subjects endpoint"""
    print("🧪 Testing /study/subjects endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/study/subjects")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ CORS Headers: {dict(response.headers)}")
        
        # Check structure
        if "subjects" not in data:
            print("❌ Missing 'subjects' key in response")
            return False
        
        subjects = data["subjects"]
        if not isinstance(subjects, list):
            print("❌ 'subjects' is not a list")
            return False
        
        print(f"✅ Found {len(subjects)} subjects")
        
        # Check each subject structure
        for i, subject in enumerate(subjects):
            print(f"\n📚 Subject {i+1}:")
            print(f"   Code: {subject.get('code', 'MISSING')}")
            print(f"   Name: {subject.get('name', 'MISSING')}")
            print(f"   Description: {subject.get('description', 'MISSING')}")
            print(f"   Units: {subject.get('units', 'MISSING')}")
            print(f"   Total Topics: {subject.get('total_topics', 'MISSING')}")
            print(f"   Difficulty: {subject.get('difficulty', 'MISSING')}")
            
            # Check required fields
            required_fields = ['code', 'name', 'description', 'units', 'total_topics']
            for field in required_fields:
                if field not in subject:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            
            # Check units is a list
            if not isinstance(subject['units'], list):
                print(f"   ❌ 'units' is not a list: {type(subject['units'])}")
                return False
            
            # Check total_topics is a number
            if not isinstance(subject['total_topics'], int):
                print(f"   ❌ 'total_topics' is not a number: {type(subject['total_topics'])}")
                return False
        
        print("\n✅ All subjects have correct structure!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing subjects endpoint: {e}")
        return False

def test_units_endpoint():
    """Test the /study/subjects/{code}/units endpoint"""
    print("\n🧪 Testing /study/subjects/{code}/units endpoint...")
    
    try:
        # Test with the first subject
        response = requests.get("http://localhost:8000/study/subjects/315319-OPERATING%20SYSTEM/units")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        
        # Check structure
        if "units" not in data:
            print("❌ Missing 'units' key in response")
            return False
        
        units = data["units"]
        if not isinstance(units, list):
            print("❌ 'units' is not a list")
            return False
        
        print(f"✅ Found {len(units)} units")
        
        # Check each unit structure
        for i, unit in enumerate(units):
            print(f"\n📖 Unit {i+1}:")
            print(f"   Unit: {unit.get('unit', 'MISSING')}")
            print(f"   Topics: {unit.get('topics', 'MISSING')}")
            
            # Check required fields
            required_fields = ['unit', 'topics']
            for field in required_fields:
                if field not in unit:
                    print(f"   ❌ Missing required field: {field}")
                    return False
            
            # Check topics is a list
            if not isinstance(unit['topics'], list):
                print(f"   ❌ 'topics' is not a list: {type(unit['topics'])}")
                return False
            
            print(f"   ✅ {len(unit['topics'])} topics found")
        
        print("\n✅ All units have correct structure!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing units endpoint: {e}")
        return False

def main():
    print("🔍 API Structure Test")
    print("=" * 40)
    
    # Test subjects endpoint
    subjects_ok = test_subjects_endpoint()
    
    # Test units endpoint
    units_ok = test_units_endpoint()
    
    print("\n📊 Test Results:")
    print(f"Subjects Endpoint: {'✅ PASS' if subjects_ok else '❌ FAIL'}")
    print(f"Units Endpoint: {'✅ PASS' if units_ok else '❌ FAIL'}")
    
    if subjects_ok and units_ok:
        print("\n🎉 All tests passed! The API structure matches frontend expectations.")
        print("The frontend should now work without the 'length' error.")
    else:
        print("\n⚠️  Some tests failed. Check the API structure.")

if __name__ == "__main__":
    main() 