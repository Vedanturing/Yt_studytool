"""
AI Configuration Settings
Configure which AI models to use based on your subscription tier
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AI Model Configuration
class AIConfig:
    # Gemini Model Settings
    # For paid users (Pro tier) - higher quotas
    GEMINI_PRO_MODEL = 'gemini-1.5-pro'
    GEMINI_2_PRO_MODEL = 'gemini-2.0-pro'
    GEMINI_2_FLASH_MODEL = 'gemini-2.0-flash'
    
    # For free users - limited quotas (50 requests/day)
    GEMINI_FREE_MODEL = 'gemini-1.5-flash'
    
    # Current model to use
    # Change this based on your subscription:
    # - Use GEMINI_PRO_MODEL for paid/Pro users
    # - Use GEMINI_FREE_MODEL for free tier users
    CURRENT_GEMINI_MODEL = GEMINI_2_FLASH_MODEL  # Changed to free tier since Pro is hitting quotas
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Quota Information
    GEMINI_FREE_QUOTA = 50  # requests per day for free tier
    GEMINI_PRO_QUOTA = "Unlimited"  # for paid users
    
    @classmethod
    def get_gemini_model(cls):
        """Get the current Gemini model to use"""
        return cls.CURRENT_GEMINI_MODEL
    
    @classmethod
    def is_paid_user(cls):
        """Check if using paid model"""
        return cls.CURRENT_GEMINI_MODEL == cls.GEMINI_PRO_MODEL
    
    @classmethod
    def get_quota_info(cls):
        """Get quota information for current tier"""
        if cls.is_paid_user():
            return f"Pro Tier: {cls.GEMINI_PRO_QUOTA} requests"
        else:
            return f"Free Tier: {cls.GEMINI_FREE_QUOTA} requests per day" 