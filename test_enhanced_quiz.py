#!/usr/bin/env python3
"""
Test script for enhanced quiz generation with different question counts
"""

import requests
import json

def test_enhanced_quiz_generation():
    """Test quiz generation with different question counts"""
    base_url = "http://localhost:8000"
    
    # Test data
    test_data = {
        "subject": "315319-OPERATING SYSTEM",
        "units": ["Unit 1", "Unit 2"],
        "difficulty": "medium",
        "question_types": ["mcq", "true_false"]
    }
    
    # Test different question counts
    question_counts = [10, 20, 35, 50]
    
    print("🧪 Testing Enhanced Quiz Generation")
    print("=" * 50)
    
    for count in question_counts:
        print(f"\n📊 Testing with {count} questions...")
        
        test_data["num_questions"] = count
        
        try:
            response = requests.post(f"{base_url}/study/generate_quiz", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                actual_count = result.get("total_questions", 0)
                unique_questions = result.get("unique_questions", False)
                questions_per_unit = result.get("questions_per_unit", 0)
                
                print(f"✅ Successfully generated {actual_count} questions")
                print(f"📋 Unique questions: {unique_questions}")
                print(f"📚 Units covered: {result.get('units', [])}")
                print(f"📊 Questions per unit: {questions_per_unit}")
                
                # Check question distribution
                questions = result.get("questions", [])
                if questions:
                    concepts = set(q.get("concept", "") for q in questions)
                    print(f"🎯 Concepts covered: {len(concepts)}")
                    print(f"📝 Sample concepts: {list(concepts)[:5]}")
                    
                    # Check if questions are unique
                    question_texts = [q.get("question", "") for q in questions]
                    unique_texts = set(question_texts)
                    print(f"🔄 Unique question texts: {len(unique_texts)} out of {len(questions)}")
                    
                    # Show sample questions
                    print(f"📝 Sample questions:")
                    for i, q in enumerate(questions[:3]):
                        print(f"   {i+1}. {q.get('question', '')[:60]}...")
                
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test with single unit to see maximum available
    print(f"\n🔍 Testing single unit (Unit 1) with 50 questions...")
    test_data["units"] = ["Unit 1"]
    test_data["num_questions"] = 50
    
    try:
        response = requests.post(f"{base_url}/study/generate_quiz", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            actual_count = result.get("total_questions", 0)
            print(f"✅ Unit 1 can generate up to {actual_count} questions")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced quiz generation test completed!")

if __name__ == "__main__":
    test_enhanced_quiz_generation() 