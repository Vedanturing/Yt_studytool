import os
import json
import subprocess
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Video Search API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class VideoRequest(BaseModel):
    keyword: str

class Comment(BaseModel):
    text: str
    author: str
    likes: int = 0

class Video(BaseModel):
    title: str
    video_url: str
    views: int
    likes: int
    description: str
    comment_count: int
    top_comments: List[Comment]
    thumbnail_url: str = ""

class VideoResponse(BaseModel):
    videos: List[Video]
    total_count: int
    source: str  # "api" or "yt-dlp"
    keyword: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/get_videos", response_model=VideoResponse)
async def get_videos(request: VideoRequest):
    """Get top 50 YouTube videos for a keyword"""
    try:
        # For now, return mock data to test the frontend
        mock_videos = [
            Video(
                title="Sample YouTube Video",
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                views=1000000,
                likes=50000,
                description="This is a sample video description for testing purposes.",
                comment_count=1000,
                top_comments=[
                    Comment(text="Great video!", author="User1", likes=10),
                    Comment(text="Amazing content!", author="User2", likes=5)
                ],
                thumbnail_url="https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
            ),
            Video(
                title="Another Sample Video",
                video_url="https://www.youtube.com/watch?v=9bZkp7q19f0",
                views=2000000,
                likes=75000,
                description="Another sample video for testing the application.",
                comment_count=1500,
                top_comments=[
                    Comment(text="Awesome!", author="User3", likes=15),
                    Comment(text="Love this!", author="User4", likes=8)
                ],
                thumbnail_url="https://img.youtube.com/vi/9bZkp7q19f0/hqdefault.jpg"
            )
        ]
        
        return VideoResponse(
            videos=mock_videos,
            total_count=len(mock_videos),
            source="mock",
            keyword=request.keyword
        )
        
    except Exception as e:
        logger.error(f"Error in get_videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 