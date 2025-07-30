#!/usr/bin/env python3
"""
Check Gemini API Status
Helps you verify your API key and configure the correct model
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

load_dotenv()

def check_gemini_status():
    """Check Gemini API status and configuration"""
    print("🔍 Checking Gemini API Status")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        print("Please add your API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Try to import and test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test with different models
        models_to_test = ['gemini-1.5-pro', 'gemini-1.5-flash']
        
        for model_name in models_to_test:
            try:
                print(f"\n🧪 Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                
                # Simple test prompt
                response = model.generate_content("Hello, this is a test.")
                
                if response.text:
                    print(f"✅ {model_name} is working!")
                    
                    # Check if this is a paid model
                    if model_name == 'gemini-1.5-pro':
                        print("💰 This appears to be a Pro/paid model")
                        print("   You should have higher quotas available")
                    else:
                        print("🆓 This is the free tier model")
                        print("   Limited to 50 requests per day")
                        
                else:
                    print(f"❌ {model_name} returned empty response")
                    
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower():
                    print(f"⚠️  {model_name} quota exceeded: {error_msg}")
                elif "not found" in error_msg.lower():
                    print(f"❌ {model_name} not available: {error_msg}")
                else:
                    print(f"❌ {model_name} error: {error_msg}")
        
        # Configuration recommendation
        print("\n" + "=" * 50)
        print("🎯 Configuration Recommendation:")
        
        if "gemini-1.5-pro" in str(response):
            print("✅ Use gemini-1.5-pro for unlimited requests")
            print("   Edit backend/ai_config.py and set:")
            print("   CURRENT_GEMINI_MODEL = GEMINI_PRO_MODEL")
        else:
            print("⚠️  Use gemini-1.5-flash for free tier")
            print("   Edit backend/ai_config.py and set:")
            print("   CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL")
        
        return True
        
    except ImportError:
        print("❌ google.generativeai not installed")
        print("Install it with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        return False

def show_config_help():
    """Show help for configuring the AI models"""
    print("\n📋 Configuration Help:")
    print("=" * 50)
    print("1. For Paid/Pro Users (Unlimited Quotas):")
    print("   Edit backend/ai_config.py")
    print("   Set: CURRENT_GEMINI_MODEL = GEMINI_PRO_MODEL")
    print()
    print("2. For Free Users (50 requests/day):")
    print("   Edit backend/ai_config.py")
    print("   Set: CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL")
    print()
    print("3. Check your current configuration:")
    print("   python check_gemini_status.py")

if __name__ == "__main__":
    success = check_gemini_status()
    if success:
        show_config_help()
    else:
        print("\n❌ Please fix the issues above and try again.") 