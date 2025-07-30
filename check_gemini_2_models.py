#!/usr/bin/env python3
"""
Check Gemini 2.0 Models
Tests available Gemini 2.0 models and their quota status
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

load_dotenv()

def check_gemini_2_models():
    """Check available Gemini 2.0 models"""
    print("🔍 Checking Gemini 2.0 Models")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # List of Gemini 2.0 models to test
        gemini_2_models = [
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash',
            'gemini-2.0-pro',
            'gemini-1.5-flash',
            'gemini-1.5-pro'
        ]
        
        working_models = []
        
        for model_name in gemini_2_models:
            try:
                print(f"\n🧪 Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                
                # Simple test prompt
                response = model.generate_content("Hello, this is a test.")
                
                if response.text:
                    print(f"✅ {model_name} is working!")
                    working_models.append(model_name)
                    
                    # Determine tier based on model name
                    if "2.0" in model_name:
                        if "pro" in model_name:
                            print("💰 Gemini 2.0 Pro - Paid tier with higher quotas")
                        elif "flash" in model_name:
                            print("⚡ Gemini 2.0 Flash - Fast model, check quotas")
                    elif "1.5" in model_name:
                        if "pro" in model_name:
                            print("💰 Gemini 1.5 Pro - Paid tier")
                        else:
                            print("🆓 Gemini 1.5 Flash - Free tier (50/day)")
                else:
                    print(f"❌ {model_name} returned empty response")
                    
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower():
                    print(f"⚠️  {model_name} quota exceeded: {error_msg}")
                elif "not found" in error_msg.lower() or "doesn't exist" in error_msg.lower():
                    print(f"❌ {model_name} not available: {error_msg}")
                else:
                    print(f"❌ {model_name} error: {error_msg}")
        
        # Recommendations
        print("\n" + "=" * 50)
        print("🎯 Gemini 2.0 Model Recommendations:")
        
        if 'gemini-2.0-pro' in working_models:
            print("🥇 BEST: Use gemini-2.0-pro for maximum performance")
            print("   - Latest model with best capabilities")
            print("   - Higher quotas for paid users")
        elif 'gemini-2.0-flash' in working_models:
            print("🥈 GOOD: Use gemini-2.0-flash for fast responses")
            print("   - Fast and efficient model")
            print("   - Check your quota limits")
        elif 'gemini-1.5-pro' in working_models:
            print("🥉 OKAY: Use gemini-1.5-pro as fallback")
            print("   - Stable and reliable")
            print("   - Paid tier required")
        elif 'gemini-1.5-flash' in working_models:
            print("📝 BASIC: Use gemini-1.5-flash for free tier")
            print("   - Limited to 50 requests/day")
            print("   - Good for testing")
        
        return working_models
        
    except ImportError:
        print("❌ google.generativeai not installed")
        return False
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

def update_config_with_best_model(working_models):
    """Update the AI config with the best available model"""
    print("\n🔧 Updating Configuration...")
    
    best_model = None
    
    # Priority order for models
    priority_models = [
        'gemini-2.0-pro',
        'gemini-2.0-flash',
        'gemini-1.5-pro',
        'gemini-1.5-flash'
    ]
    
    for model in priority_models:
        if model in working_models:
            best_model = model
            break
    
    if best_model:
        print(f"✅ Recommended model: {best_model}")
        
        # Update the config file
        config_path = "backend/ai_config.py"
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update the model configuration
            if "2.0" in best_model:
                # Add new 2.0 model constants
                if "GEMINI_2_PRO_MODEL" not in content:
                    content = content.replace(
                        "GEMINI_PRO_MODEL = 'gemini-1.5-pro'",
                        "GEMINI_PRO_MODEL = 'gemini-1.5-pro'\n    GEMINI_2_PRO_MODEL = 'gemini-2.0-pro'\n    GEMINI_2_FLASH_MODEL = 'gemini-2.0-flash'"
                    )
                
                # Set current model to 2.0 version
                if "pro" in best_model:
                    content = content.replace(
                        "CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL",
                        "CURRENT_GEMINI_MODEL = GEMINI_2_PRO_MODEL"
                    )
                else:
                    content = content.replace(
                        "CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL",
                        "CURRENT_GEMINI_MODEL = GEMINI_2_FLASH_MODEL"
                    )
            else:
                # Use 1.5 models
                if "pro" in best_model:
                    content = content.replace(
                        "CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL",
                        "CURRENT_GEMINI_MODEL = GEMINI_PRO_MODEL"
                    )
                else:
                    content = content.replace(
                        "CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL",
                        "CURRENT_GEMINI_MODEL = GEMINI_FREE_MODEL"
                    )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {config_path} to use {best_model}")
            print("🔄 Restart your Flask server to apply changes")
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
    else:
        print("❌ No working models found")

if __name__ == "__main__":
    working_models = check_gemini_2_models()
    if working_models:
        update_config_with_best_model(working_models)
    else:
        print("\n❌ No Gemini models are working. Check your API key and quota.") 