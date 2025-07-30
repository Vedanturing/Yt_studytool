#!/usr/bin/env python3
"""
Test AI Functionality
Tests the web scraper and AI quiz generator functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

load_dotenv()

def test_ai_setup():
    """Test AI API setup and functionality"""
    print("🤖 Testing AI Functionality Setup")
    print("=" * 50)
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"Gemini API Key: {'✅ Set' if gemini_key else '❌ Not set'}")
    
    if not openai_key and not gemini_key:
        print("\n⚠️  No AI API keys found!")
        print("To enable AI-powered quiz generation, please:")
        print("1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
        print("3. Add them to your .env file:")
        print("   OPENAI_API_KEY=your_openai_key_here")
        print("   GEMINI_API_KEY=your_gemini_key_here")
        print("\nThe system will use fallback questions if no API keys are available.")
    
    # Test imports
    try:
        from backend.web_scraper import StudyMaterialScraper
        print("✅ Web scraper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import web scraper: {e}")
    
    try:
        from backend.ai_quiz_generator import AIQuizGenerator
        print("✅ AI quiz generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI quiz generator: {e}")
    
    # Test web scraper
    print("\n🔍 Testing Web Scraper...")
    try:
        scraper = StudyMaterialScraper()
        materials = scraper.search_study_materials(
            subject="Operating System",
            unit="Unit 1",
            topics=["Process Management", "Memory Management"]
        )
        print(f"✅ Web scraper test completed")
        print(f"   Found {len(materials.get('articles', []))} articles")
        print(f"   Found {len(materials.get('videos', []))} videos")
        print(f"   Found {len(materials.get('notes', []))} notes")
    except Exception as e:
        print(f"❌ Web scraper test failed: {e}")
    
    # Test AI quiz generator
    print("\n🤖 Testing AI Quiz Generator...")
    try:
        quiz_gen = AIQuizGenerator()
        questions = quiz_gen.generate_quiz_questions(
            subject="Operating System",
            unit="Unit 1",
            topics=["Process Management", "Memory Management"],
            num_questions=3,
            difficulty="medium"
        )
        print(f"✅ AI quiz generator test completed")
        print(f"   Generated {len(questions)} questions")
        
        if questions:
            print("\n📝 Sample Question:")
            q = questions[0]
            print(f"   Question: {q['question']}")
            print(f"   Options: {q['options']}")
            print(f"   Correct: {q['correct_answer']}")
            print(f"   Concept: {q['concept']}")
    except Exception as e:
        print(f"❌ AI quiz generator test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("- Web scraper will find real study materials from educational websites")
    print("- AI quiz generator will create intelligent questions based on topics")
    print("- Both have fallback modes if APIs are not available")
    print("- Set up API keys for the best experience!")

if __name__ == "__main__":
    test_ai_setup() 