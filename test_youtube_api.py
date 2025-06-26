#!/usr/bin/env python3
"""
Test YouTube API key directly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_youtube_api_key():
    """Test if the YouTube API key is valid and working"""
    print("🔍 Testing YouTube API Key...")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        print("❌ No YouTube API key found in .env file")
        print("   Please add your YouTube API key to the .env file:")
        print("   YOUTUBE_API_KEY=your_actual_api_key_here")
        return False
    
    if api_key == "your_youtube_api_key_here":
        print("❌ YouTube API key is still the placeholder value")
        print("   Please replace 'your_youtube_api_key_here' with your actual API key")
        return False
    
    # Test the API key with a simple search
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": "python programming",
            "type": "video",
            "maxResults": 1,  # Just test with 1 result
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                print("✅ YouTube API key is valid and working!")
                print(f"   Found video: {data['items'][0]['snippet']['title']}")
                return True
            else:
                print("⚠️  API key works but no results found")
                return True
        elif response.status_code == 403:
            print("❌ YouTube API key is invalid or quota exceeded")
            print("   Please check your API key and quota in Google Cloud Console")
            return False
        elif response.status_code == 400:
            print("❌ YouTube API key is invalid")
            print("   Please check your API key format")
            return False
        else:
            print(f"❌ Unexpected API response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out. Check your internet connection.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_quota():
    """Test API quota by making a request for 15 videos"""
    print("\n🔍 Testing API quota with 15 videos request...")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key or api_key == "your_youtube_api_key_here":
        print("⚠️  Skipping quota test - no valid API key")
        return False
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": "python programming",
            "type": "video",
            "maxResults": 15,  # Test with 15 videos
            "order": "viewCount",
            "key": api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"✅ Successfully fetched {len(items)} videos")
            print(f"   Quota remaining: {response.headers.get('X-RateLimit-Remaining', 'Unknown')}")
            return True
        elif response.status_code == 403:
            print("❌ API quota exceeded or key invalid")
            print("   This is expected if using a free tier API key")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Quota test error: {e}")
        return False

def main():
    """Run YouTube API tests"""
    print("🧪 YouTube API Key Validation")
    print("=" * 50)
    
    # Test API key validity
    key_valid = test_youtube_api_key()
    
    # Test quota (only if key is valid)
    if key_valid:
        test_api_quota()
    
    print("\n" + "=" * 50)
    if key_valid:
        print("✅ YouTube API key is ready to use!")
        print("   The backend will use the API for fetching videos.")
    else:
        print("⚠️  YouTube API key needs to be configured.")
        print("   The backend will fallback to yt-dlp for fetching videos.")
    
    print("\n📝 Next steps:")
    print("   1. If API key is invalid, get one from Google Cloud Console")
    print("   2. Add it to your .env file")
    print("   3. Restart the backend to use the API")

if __name__ == "__main__":
    main() 