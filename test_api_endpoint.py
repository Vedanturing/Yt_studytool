#!/usr/bin/env python3
"""
Test script for the enhanced study material API endpoint
"""

import requests
import json

def test_enhanced_study_material_api():
    """Test the enhanced study material generation API endpoint"""
    
    # API endpoint
    url = "http://localhost:5000/study/generate_enhanced_study_material"
    
    # Test data
    data = {
        "subject": "OPERATING SYSTEM",
        "units": ["Unit 1: Introduction to Operating Systems"]
    }
    
    try:
        print("🚀 Testing Enhanced Study Material API Endpoint")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 50)
        
        # Make the request
        response = requests.post(url, json=data, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"Subject: {result.get('subject')}")
            print(f"Generator Type: {result.get('generator_type')}")
            
            study_materials = result.get('study_materials', {})
            for unit, materials in study_materials.items():
                print(f"\n📚 Unit: {unit}")
                print(f"   Articles: {len(materials.get('articles', []))}")
                print(f"   Videos: {len(materials.get('videos', []))}")
                print(f"   Notes: {len(materials.get('notes', []))}")
                
                # Show sample videos
                videos = materials.get('videos', [])
                if videos:
                    print("\n🎥 Sample Videos:")
                    for i, video in enumerate(videos[:3]):
                        print(f"   {i+1}. {video.get('title', 'Unknown')}")
                        print(f"      Source: {video.get('source', 'Unknown')}")
                        print(f"      Duration: {video.get('duration', 'Unknown')} seconds")
                        print(f"      Uploader: {video.get('uploader', 'Unknown')}")
            
            return True
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running on port 5000.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The server might be processing the request.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Study Material API")
    print("=" * 50)
    
    # Test health endpoint first
    if test_health_endpoint():
        print("\n" + "=" * 50)
        # Test enhanced study material endpoint
        test_enhanced_study_material_api()
    else:
        print("❌ Server is not running. Please start the Flask app first.") 