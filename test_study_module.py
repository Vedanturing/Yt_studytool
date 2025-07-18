#!/usr/bin/env python3
"""
Test script for the Study Module
Tests all major functionality including subject loading, study material generation, quiz generation, and report generation.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
STUDY_BASE_URL = f"{BASE_URL}/study"

def test_health_check():
    """Test if the backend is running"""
    print("\n🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_subjects():
    """Test getting available subjects"""
    print("\n📚 Testing subject loading...")
    try:
        response = requests.get(f"{STUDY_BASE_URL}/subjects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            subjects = data.get('subjects', [])
            print(f"✅ Loaded {len(subjects)} subjects:")
            for subject in subjects:
                print(f"   - {subject['code']}: {subject['name']} ({len(subject['units'])} units)")
            return subjects
        else:
            print(f"❌ Failed to load subjects: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Subject loading error: {e}")
        return []

def test_get_subject_units(subject_code):
    """Test getting units for a specific subject"""
    print(f"\n📖 Testing unit loading for {subject_code}...")
    try:
        response = requests.get(f"{STUDY_BASE_URL}/subjects/{subject_code}/units", timeout=10)
        if response.status_code == 200:
            data = response.json()
            units = data.get('units', [])
            print(f"✅ Loaded {len(units)} units for {data['subject_name']}:")
            for unit in units:
                print(f"   - {unit['unit']}: {len(unit['topics'])} topics")
            return units
        else:
            print(f"❌ Failed to load units: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Unit loading error: {e}")
        return []

def test_generate_study_material(subject_code, units):
    """Test study material generation"""
    print(f"\n📚 Testing study material generation for {subject_code}...")
    try:
        response = requests.post(
            f"{STUDY_BASE_URL}/generate_study_material",
            json={
                "subject": subject_code,
                "units": units
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            study_materials = data.get('study_materials', {})
            print(f"✅ Generated study materials for {len(study_materials)} units:")
            for unit, materials in study_materials.items():
                total_resources = (
                    len(materials.get('articles', [])) +
                    len(materials.get('videos', [])) +
                    len(materials.get('notes', []))
                )
                print(f"   - {unit}: {total_resources} resources")
            return study_materials
        else:
            print(f"❌ Failed to generate study materials: {response.status_code}")
            print(f"   Response: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Study material generation error: {e}")
        return {}

def test_generate_quiz(subject_code, units):
    """Test quiz generation"""
    print(f"\n🧠 Testing quiz generation for {subject_code}...")
    try:
        response = requests.post(
            f"{STUDY_BASE_URL}/generate_quiz",
            json={
                "subject": subject_code,
                "units": units,
                "num_questions": 5,
                "difficulty": "medium",
                "question_types": ["mcq", "true_false"]
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            print(f"✅ Generated {len(questions)} quiz questions:")
            for i, question in enumerate(questions[:3]):  # Show first 3 questions
                print(f"   {i+1}. {question['question'][:100]}...")
            return questions
        else:
            print(f"❌ Failed to generate quiz: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        return []

def test_evaluate_quiz(subject_code, unit, questions):
    """Test quiz evaluation"""
    print(f"\n📊 Testing quiz evaluation...")
    try:
        # Create mock responses (all correct for testing)
        responses = {}
        for i, question in enumerate(questions):
            responses[i] = question['correct_answer']
        
        response = requests.post(
            f"{STUDY_BASE_URL}/evaluate_quiz",
            json={
                "subject": subject_code,
                "unit": unit,
                "responses": responses
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            score = data.get('score', 0)
            mistakes = data.get('mistakes', [])
            print(f"✅ Quiz evaluation completed:")
            print(f"   - Score: {score:.1f}%")
            print(f"   - Correct: {data.get('correct_count', 0)}/{data.get('total_questions', 0)}")
            print(f"   - Mistakes: {len(mistakes)}")
            return data
        else:
            print(f"❌ Failed to evaluate quiz: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Quiz evaluation error: {e}")
        return None

def test_generate_report(subject_code, unit, evaluation_result):
    """Test report generation"""
    print(f"\n📄 Testing report generation...")
    try:
        response = requests.post(
            f"{STUDY_BASE_URL}/generate_report",
            json={
                "subject": subject_code,
                "unit": unit,
                "evaluation_result": evaluation_result
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Report generated successfully:")
            print(f"   - Filename: {data.get('report_filename', 'N/A')}")
            print(f"   - Path: {data.get('report_path', 'N/A')}")
            return data
        else:
            print(f"❌ Failed to generate report: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return None

def test_full_study_flow():
    """Test the complete study flow"""
    print("🎓 Testing Complete Study Module Flow")
    print("=" * 50)
    
    # Step 1: Health check
    if not test_health_check():
        print("❌ Backend not available. Please start the backend server.")
        return False
    
    # Step 2: Get subjects
    subjects = test_get_subjects()
    if not subjects:
        print("❌ No subjects available.")
        return False
    
    # Step 3: Get units for first subject
    subject_code = subjects[0]['code']
    units = test_get_subject_units(subject_code)
    if not units:
        print("❌ No units available.")
        return False
    
    # Step 4: Generate study materials
    selected_units = [units[0]['unit']]  # Use first unit
    study_materials = test_generate_study_material(subject_code, selected_units)
    
    # Step 5: Generate quiz
    quiz_questions = test_generate_quiz(subject_code, selected_units)
    if not quiz_questions:
        print("❌ No quiz questions generated.")
        return False
    
    # Step 6: Evaluate quiz
    evaluation_result = test_evaluate_quiz(subject_code, selected_units[0], quiz_questions)
    if not evaluation_result:
        print("❌ Quiz evaluation failed.")
        return False
    
    # Step 7: Generate report
    report_result = test_generate_report(subject_code, selected_units[0], evaluation_result)
    
    print("\n" + "=" * 50)
    print("🎉 Study Module Test Summary:")
    print(f"✅ Subjects loaded: {len(subjects)}")
    print(f"✅ Units loaded: {len(units)}")
    print(f"✅ Study materials generated: {len(study_materials)}")
    print(f"✅ Quiz questions generated: {len(quiz_questions)}")
    print(f"✅ Quiz evaluated: {evaluation_result['score']:.1f}%")
    print(f"✅ Report generated: {'Yes' if report_result else 'No'}")
    
    return True

def test_error_handling():
    """Test error handling scenarios"""
    print("\n⚠️ Testing Error Handling")
    print("=" * 30)
    
    # Test invalid subject
    print("\nTesting invalid subject...")
    try:
        response = requests.get(f"{STUDY_BASE_URL}/subjects/INVALID-SUBJECT/units", timeout=10)
        if response.status_code == 404:
            print("✅ Correctly handled invalid subject")
        else:
            print(f"❌ Unexpected response for invalid subject: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid subject: {e}")
    
    # Test empty units
    print("\nTesting empty units...")
    try:
        response = requests.post(
            f"{STUDY_BASE_URL}/generate_study_material",
            json={
                "subject": "315319-OPERATING SYSTEM",
                "units": []
            },
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Correctly handled empty units")
        else:
            print(f"❌ Unexpected response for empty units: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing empty units: {e}")

if __name__ == "__main__":
    print("🚀 Starting Study Module Tests")
    print(f"📡 Testing against: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run full flow test
        success = test_full_study_flow()
        
        if success:
            # Run error handling tests
            test_error_handling()
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Study Module Tests Completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}") 