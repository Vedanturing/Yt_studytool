#!/usr/bin/env python3
"""
Test script for offline quiz archiving functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_offline_functionality():
    print("🧪 Testing Offline Quiz Archiving Functionality")
    print("=" * 50)
    
    # Test 1: Generate a quiz (should save to storage)
    print("\n1. Testing quiz generation and storage...")
    try:
        response = requests.post(f"{BASE_URL}/generate_quiz", json={
            "topics": ["Machine Learning", "Neural Networks"],
            "num_questions": 5,
            "difficulty": "medium",
            "question_types": ["mcq", "true_false"],
            "subject": "Computer Science"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quiz generated successfully!")
            print(f"   - Questions: {data.get('total_questions', 0)}")
            print(f"   - Source: {data.get('source', 'unknown')}")
            print(f"   - Topics: {data.get('topics_covered', [])}")
        else:
            print(f"❌ Failed to generate quiz: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        return False
    
    # Test 2: Get available quizzes
    print("\n2. Testing available quizzes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/available_quizzes")
        
        if response.status_code == 200:
            data = response.json()
            quizzes = data.get('quizzes', [])
            print(f"✅ Found {len(quizzes)} available quizzes")
            
            for quiz in quizzes[:3]:  # Show first 3
                print(f"   - {quiz.get('topic', 'Unknown')} ({quiz.get('subject', 'Unknown')})")
        else:
            print(f"❌ Failed to get available quizzes: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting available quizzes: {e}")
    
    # Test 3: Load a specific quiz
    print("\n3. Testing quiz loading...")
    try:
        response = requests.get(f"{BASE_URL}/load_quiz/Computer%20Science/Unit%201/Machine%20Learning")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quiz loaded successfully!")
            print(f"   - Subject: {data.get('subject', 'Unknown')}")
            print(f"   - Topic: {data.get('topic', 'Unknown')}")
            print(f"   - Questions: {len(data.get('questions', []))}")
        else:
            print(f"❌ Failed to load quiz: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error loading quiz: {e}")
    
    # Test 4: Save study material
    print("\n4. Testing study material saving...")
    try:
        response = requests.post(f"{BASE_URL}/save_study_material", data={
            "subject": "Computer Science",
            "topic": "Machine Learning",
            "material_type": "note",
            "title": "ML Basics Notes",
            "url": "https://example.com/ml-notes"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Study material saved successfully!")
            print(f"   - Title: {data.get('title', 'Unknown')}")
            print(f"   - Subject: {data.get('subject', 'Unknown')}")
        else:
            print(f"❌ Failed to save study material: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error saving study material: {e}")
    
    # Test 5: Get study materials
    print("\n5. Testing study material retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/get_study_materials/Computer%20Science/Machine%20Learning")
        
        if response.status_code == 200:
            data = response.json()
            materials = data.get('materials', [])
            print(f"✅ Found {len(materials)} study materials")
            
            for material in materials:
                print(f"   - {material.get('title', 'Unknown')} ({material.get('material_type', 'Unknown')})")
        else:
            print(f"❌ Failed to get study materials: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting study materials: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Offline functionality test completed!")
    return True

if __name__ == "__main__":
    # Wait a moment for the server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    test_offline_functionality() 