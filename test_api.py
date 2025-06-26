#!/usr/bin/env python3
"""
Test script for the YouTube Video Search API
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_videos_endpoint():
    """Test the get_videos endpoint"""
    print("\n🔍 Testing get_videos endpoint...")
    
    test_keywords = [
        "python programming",
        "machine learning",
        "web development"
    ]
    
    for keyword in test_keywords:
        print(f"\n📝 Testing keyword: '{keyword}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/get_videos",
                json={"keyword": keyword},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                total_count = data.get("total_count", 0)
                source = data.get("source", "unknown")
                
                print(f"✅ Success! Found {total_count} videos (source: {source})")
                
                # Check if we got the expected number of videos (up to 15)
                if total_count > 0 and total_count <= 15:
                    print(f"✅ Video count is within expected range (1-15)")
                else:
                    print(f"⚠️  Unexpected video count: {total_count}")
                
                # Show first video details
                if videos:
                    first_video = videos[0]
                    print(f"📺 First video: {first_video.get('title', 'No title')}")
                    print(f"👀 Views: {first_video.get('views', 0):,}")
                    print(f"👍 Likes: {first_video.get('likes', 0):,}")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out for keyword: {keyword}")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to backend. Make sure it's running on port 8000.")
            return False
        except Exception as e:
            print(f"❌ Error testing keyword '{keyword}': {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    return True

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing error handling...")
    
    # Test with empty keyword
    try:
        response = requests.post(
            "http://localhost:8000/get_videos",
            json={"keyword": ""},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Empty keyword properly rejected")
        else:
            print(f"⚠️  Empty keyword returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing empty keyword: {e}")
    
    # Test with missing keyword
    try:
        response = requests.post(
            "http://localhost:8000/get_videos",
            json={},
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Missing keyword properly rejected")
        else:
            print(f"⚠️  Missing keyword returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing missing keyword: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting API Tests...")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health check failed. Backend may not be running.")
        return
    
    # Test get_videos endpoint
    test_get_videos_endpoint()
    
    # Test error handling
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ API tests completed!")

if __name__ == "__main__":
    main() 