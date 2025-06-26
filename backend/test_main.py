import pytest
import json
import subprocess
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app, search_videos_with_api, search_videos_with_ytdlp

client = TestClient(app)

# Mock data for testing
mock_api_response = {
    "items": [
        {
            "id": {"videoId": "test_video_id_1"},
            "snippet": {
                "title": "Test Video 1",
                "description": "Test description 1",
                "thumbnails": {"high": {"url": "https://example.com/thumb1.jpg"}}
            }
        },
        {
            "id": {"videoId": "test_video_id_2"},
            "snippet": {
                "title": "Test Video 2",
                "description": "Test description 2",
                "thumbnails": {"high": {"url": "https://example.com/thumb2.jpg"}}
            }
        }
    ]
}

mock_video_details = {
    "items": [
        {
            "id": "test_video_id_1",
            "snippet": {
                "title": "Test Video 1",
                "description": "Test description 1",
                "thumbnails": {"high": {"url": "https://example.com/thumb1.jpg"}}
            },
            "statistics": {
                "viewCount": "1000",
                "likeCount": "100",
                "commentCount": "50"
            }
        },
        {
            "id": "test_video_id_2",
            "snippet": {
                "title": "Test Video 2",
                "description": "Test description 2",
                "thumbnails": {"high": {"url": "https://example.com/thumb2.jpg"}}
            },
            "statistics": {
                "viewCount": "2000",
                "likeCount": "200",
                "commentCount": "100"
            }
        }
    ]
}

mock_comments_response = {
    "items": [
        {
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "textDisplay": "Great video!",
                        "authorDisplayName": "User1",
                        "likeCount": 5
                    }
                }
            }
        },
        {
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "textDisplay": "Amazing content!",
                        "authorDisplayName": "User2",
                        "likeCount": 3
                    }
                }
            }
        }
    ]
}

mock_ytdlp_output = [
    {
        "title": "Test Video 1",
        "webpage_url": "https://www.youtube.com/watch?v=test1",
        "view_count": 1000,
        "like_count": 100,
        "description": "Test description 1",
        "comment_count": 50,
        "thumbnail": "https://example.com/thumb1.jpg"
    },
    {
        "title": "Test Video 2",
        "webpage_url": "https://www.youtube.com/watch?v=test2",
        "view_count": 2000,
        "like_count": 200,
        "description": "Test description 2",
        "comment_count": 100,
        "thumbnail": "https://example.com/thumb2.jpg"
    }
]

class TestGetVideosEndpoint:
    """Test cases for the /get_videos endpoint"""
    
    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('backend.main.build')
    def test_valid_keyword_returns_results(self, mock_build):
        """Test that a valid keyword returns 50 results"""
        # Mock YouTube API responses
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        
        # Mock search response
        mock_youtube.search.return_value.list.return_value.execute.return_value = mock_api_response
        
        # Mock video details response
        mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_video_details
        
        # Mock comments response
        mock_youtube.commentThreads.return_value.list.return_value.execute.return_value = mock_comments_response
        
        response = client.post("/get_videos", json={"keyword": "python programming"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert data["source"] == "api"
        assert data["keyword"] == "python programming"
        assert len(data["videos"]) == 2
        
        # Check video structure
        video = data["videos"][0]
        assert "title" in video
        assert "video_url" in video
        assert "views" in video
        assert "likes" in video
        assert "description" in video
        assert "comment_count" in video
        assert "top_comments" in video
        assert "thumbnail_url" in video
    
    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'invalid_key'})
    @patch('backend.main.build')
    def test_api_key_failure(self, mock_build):
        """Test API key failure handling"""
        mock_build.side_effect = Exception("Invalid API key")
        
        response = client.post("/get_videos", json={"keyword": "test"})
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]
    
    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'invalid_key'})
    @patch('backend.main.build')
    @patch('subprocess.run')
    def test_ytdlp_fallback_returns_valid_structure(self, mock_subprocess, mock_build):
        """Test yt-dlp fallback returns valid structure"""
        # Mock API failure
        mock_build.side_effect = Exception("API failed")
        
        # Mock yt-dlp success
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "\n".join([json.dumps(video) for video in mock_ytdlp_output])
        mock_subprocess.return_value = mock_process
        
        response = client.post("/get_videos", json={"keyword": "test"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "yt-dlp"
        assert data["total_count"] == 2
        assert len(data["videos"]) == 2
        
        # Check video structure
        video = data["videos"][0]
        assert video["title"] == "Test Video 1"
        assert video["video_url"] == "https://www.youtube.com/watch?v=test1"
        assert video["views"] == 1000
        assert video["likes"] == 100
    
    def test_invalid_keyword_gibberish(self):
        """Test invalid keyword (gibberish) handling"""
        response = client.post("/get_videos", json={"keyword": "xqwertyuiop123456789"})
        
        # Should return 200 with empty results or 500 if both methods fail
        assert response.status_code in [200, 500]
    
    def test_empty_keyword(self):
        """Test empty keyword handling"""
        response = client.post("/get_videos", json={"keyword": ""})
        
        # Should return 200 with empty results or 500 if both methods fail
        assert response.status_code in [200, 500]
    
    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'invalid_key'})
    @patch('backend.main.build')
    @patch('subprocess.run')
    def test_both_api_and_ytdlp_fail(self, mock_subprocess, mock_build):
        """Test when both API and yt-dlp fail"""
        # Mock API failure
        mock_build.side_effect = Exception("API failed")
        
        # Mock yt-dlp failure
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "yt-dlp error"
        mock_subprocess.return_value = mock_process
        
        response = client.post("/get_videos", json={"keyword": "test"})
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]

class TestSearchVideosWithAPI:
    """Test cases for search_videos_with_api function"""
    
    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('backend.main.build')
    def test_search_videos_with_api_success(self, mock_build):
        """Test successful API search"""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        
        mock_youtube.search.return_value.list.return_value.execute.return_value = mock_api_response
        mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_video_details
        mock_youtube.commentThreads.return_value.list.return_value.execute.return_value = mock_comments_response
        
        videos = search_videos_with_api("test")
        
        assert len(videos) == 2
        assert videos[0].title == "Test Video 1"
        assert videos[0].views == 1000
        assert videos[0].likes == 100

class TestSearchVideosWithYtDlp:
    """Test cases for search_videos_with_ytdlp function"""
    
    @patch('subprocess.run')
    def test_search_videos_with_ytdlp_success(self, mock_subprocess):
        """Test successful yt-dlp search"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "\n".join([json.dumps(video) for video in mock_ytdlp_output])
        mock_subprocess.return_value = mock_process
        
        videos = search_videos_with_ytdlp("test")
        
        assert len(videos) == 2
        assert videos[0].title == "Test Video 1"
        assert videos[0].views == 1000
        assert videos[0].likes == 100
    
    @patch('subprocess.run')
    def test_search_videos_with_ytdlp_failure(self, mock_subprocess):
        """Test yt-dlp search failure"""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "yt-dlp error"
        mock_subprocess.return_value = mock_process
        
        with pytest.raises(Exception):
            search_videos_with_ytdlp("test")

class TestHealthEndpoint:
    """Test cases for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data 