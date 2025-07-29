#!/usr/bin/env python3
"""
Test New Endpoints
Tests the generate_quiz and generate_study_material endpoints
"""

import requests
import json

def test_generate_study_material():
    """Test the /study/generate_study_material endpoint"""
    print("🧪 Testing /study/generate_study_material endpoint...")
    
    try:
        data = {
            "subject": "315319-OPERATING SYSTEM",
            "units": ["Unit 1", "Unit 2"]
        }
        
        response = requests.post("http://localhost:8000/study/generate_study_material", json=data)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing generate_study_material: {e}")
        return False

def test_generate_quiz():
    """Test the /study/generate_quiz endpoint"""
    print("\n🧪 Testing /study/generate_quiz endpoint...")
    
    try:
        data = {
            "subject": "315319-OPERATING SYSTEM",
            "units": ["Unit 1", "Unit 2"],
            "num_questions": 5,
            "difficulty": "medium",
            "question_types": ["mcq", "true_false"]
        }
        
        response = requests.post("http://localhost:8000/study/generate_quiz", json=data)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing generate_quiz: {e}")
        return False

def test_evaluate_quiz():
    """Test the /study/evaluate_quiz endpoint"""
    print("\n🧪 Testing /study/evaluate_quiz endpoint...")
    
    try:
        data = {
            "subject": "315319-OPERATING SYSTEM",
            "unit": "Unit 1",
            "responses": {
                "1": "Option A",
                "2": "Option B",
                "3": "Option C"
            }
        }
        
        response = requests.post("http://localhost:8000/study/evaluate_quiz", json=data)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing evaluate_quiz: {e}")
        return False

def main():
    print("🔍 Testing New Endpoints")
    print("=" * 40)
    
    # Test generate study material
    study_material_ok = test_generate_study_material()
    
    # Test generate quiz
    quiz_ok = test_generate_quiz()
    
    # Test evaluate quiz
    evaluate_ok = test_evaluate_quiz()
    
    print("\n📊 Test Results:")
    print(f"Generate Study Material: {'✅ PASS' if study_material_ok else '❌ FAIL'}")
    print(f"Generate Quiz: {'✅ PASS' if quiz_ok else '❌ FAIL'}")
    print(f"Evaluate Quiz: {'✅ PASS' if evaluate_ok else '❌ FAIL'}")
    
    if study_material_ok and quiz_ok and evaluate_ok:
        print("\n🎉 All new endpoints are working correctly!")
        print("The frontend should now be able to generate study materials and quizzes.")
    else:
        print("\n⚠️  Some endpoints failed. Check the server logs.")

if __name__ == "__main__":
    main() 