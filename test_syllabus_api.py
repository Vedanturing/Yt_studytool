#!/usr/bin/env python3
"""
Test script for the new Syllabus-Based Learning API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_syllabus_text():
    """Test syllabus upload with text content"""
    print("\n📚 Testing syllabus upload with text...")
    
    text_content = """
Unit 1: Introduction to Artificial Intelligence
1. What is Artificial Intelligence
2. History of AI
3. Types of AI Systems
4. Applications of AI

Unit 2: Machine Learning Basics
1. Introduction to Machine Learning
2. Supervised Learning
3. Unsupervised Learning
4. Reinforcement Learning

Unit 3: Neural Networks
1. Perceptrons and Neural Networks
2. Backpropagation
3. Deep Learning
4. Convolutional Neural Networks
"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/upload_syllabus",
            data={"text_content": text_content},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Syllabus upload successful!")
            print(f"   Topics found: {data['total_topics']}")
            print(f"   Units: {data['units']}")
            return data['topics']
        else:
            print(f"❌ Syllabus upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Syllabus upload error: {e}")
        return None

def test_videos_by_syllabus(topics):
    """Test getting videos for syllabus topics"""
    print("\n📹 Testing videos by syllabus...")
    
    if not topics:
        print("❌ No topics available for video search")
        return None
    
    try:
        response = requests.post(
            f"{BASE_URL}/videos_by_syllabus",
            json={"topics": topics[:3]},  # Test with first 3 topics
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Videos found successfully!")
            print(f"   Total topics: {data['total_topics']}")
            print(f"   Total videos: {data['total_videos']}")
            return data['syllabus_mapping']
        else:
            print(f"❌ Videos search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Videos search error: {e}")
        return None

def test_generate_quiz(topics):
    """Test quiz generation"""
    print("\n🧠 Testing quiz generation...")
    
    if not topics:
        print("❌ No topics available for quiz generation")
        return None
    
    topic_names = [topic['topic'] for topic in topics[:3]]
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_quiz",
            json={
                "topics": topic_names,
                "num_questions": 5,
                "question_types": ["mcq", "true_false"]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quiz generated successfully!")
            print(f"   Questions: {data['total_questions']}")
            print(f"   Topics covered: {data['topics_covered']}")
            return data['questions']
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        return None

def test_generate_report(questions, topics):
    """Test report generation"""
    print("\n📊 Testing report generation...")
    
    if not questions or not topics:
        print("❌ No questions or topics available for report generation")
        return None
    
    # Create sample quiz attempts
    quiz_attempts = []
    for i, question in enumerate(questions[:3]):
        quiz_attempts.append({
            "question": question['question'],
            "selected_answer": question['options'][0],  # Simulate user selecting first option
            "correct_answer": question['answer'],
            "is_correct": question['options'][0] == question['answer'],
            "topic": question['topic']
        })
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_report",
            json={
                "quiz_attempts": quiz_attempts,
                "watched_videos": ["https://youtube.com/watch?v=example1"],
                "syllabus_topics": topics[:3]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Report generated successfully!")
            print(f"   Overall score: {data['overall_score']:.1f}%")
            print(f"   Weak areas: {len(data['weak_areas'])}")
            print(f"   Recommendations: {len(data['recommendations'])}")
            return data
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Syllabus-Based Learning API Tests")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test syllabus upload
    topics = test_upload_syllabus_text()
    if not topics:
        print("❌ Syllabus upload failed, stopping tests")
        return
    
    # Test videos by syllabus
    video_mapping = test_videos_by_syllabus(topics)
    
    # Test quiz generation
    questions = test_generate_quiz(topics)
    
    # Test report generation
    if questions:
        report = test_generate_report(questions, topics)
    
    print("\n" + "=" * 50)
    print("🎉 Syllabus-Based Learning API Tests Completed!")
    
    if topics and video_mapping and questions:
        print("✅ All core features working!")
    else:
        print("⚠️  Some features may have issues")

if __name__ == "__main__":
    main() 