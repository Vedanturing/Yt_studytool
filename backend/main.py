import os
import json
import subprocess
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from googleapiclient.discovery import build
from dotenv import load_dotenv
import io
import tempfile
import asyncio
import urllib.parse
from pathlib import Path

# Import export libraries
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    print("Warning: Export libraries not available. Install openpyxl and reportlab for export functionality.")

# Import transcription and AI libraries
try:
    import whisper
    import openai
    from transformers import pipeline
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI libraries not available. Install whisper, openai, and transformers for transcription/summarization.")

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

# Global variables for AI models
whisper_model = None
summarizer = None

def initialize_ai_models():
    """Initialize AI models (Whisper and T5)"""
    global AI_AVAILABLE, whisper_model, summarizer
    
    try:
        logger.info("Initializing AI models...")
        
        # Test Whisper import
        import whisper
        logger.info("Whisper imported successfully")
        
        # Test transformers import
        from transformers import pipeline
        logger.info("Transformers imported successfully")
        
        # Initialize models as None (lazy loading)
        whisper_model = None
        summarizer = None
        AI_AVAILABLE = True
        
        logger.info("AI models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load AI models: {e}")
        AI_AVAILABLE = False

# Initialize models on startup
# if AI_AVAILABLE:
#     initialize_ai_models()

def get_whisper_model():
    """Lazy load Whisper model"""
    global whisper_model
    if whisper_model is None and AI_AVAILABLE:
        try:
            # Get model size from environment variable, default to 'base'
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            logger.info(f"Loading Whisper model ({model_size})...")
            whisper_model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise HTTPException(status_code=500, detail="Failed to load Whisper model")
    return whisper_model

def get_summarizer():
    """Lazy load summarization model"""
    global summarizer
    if summarizer is None and AI_AVAILABLE:
        try:
            # Get model from environment variable, default to 't5-small'
            model_name = os.getenv("SUMMARIZATION_MODEL", "t5-small")
            logger.info(f"Loading summarization model ({model_name})...")
            
            if model_name.lower() == "openai":
                # Use OpenAI API if specified
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    logger.warning("OpenAI API key not found, falling back to t5-small")
                    model_name = "t5-small"
                else:
                    # Return a special flag to use OpenAI API
                    return "openai"
            
            summarizer = pipeline("summarization", model=model_name, device=-1)
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise HTTPException(status_code=500, detail="Failed to load summarization model")
    return summarizer

# Pydantic models
class VideoRequest(BaseModel):
    keyword: str

class TranscribeRequest(BaseModel):
    video_url: str

class TranscribeResponse(BaseModel):
    transcription: str
    video_url: str
    video_title: str = ""
    duration: Optional[float] = None

class SummarizeRequest(BaseModel):
    transcription: str

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int

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

class ExportRequest(BaseModel):
    videos: List[Video]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

def generate_filename(prefix: str, extension: str, keyword: str = "") -> str:
    """Generate filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_keyword = safe_keyword.replace(' ', '_')[:20]  # Limit length
    return f"{prefix}_{safe_keyword}_{timestamp}.{extension}"

def create_excel_file(videos: List[Video], keyword: str = "") -> bytes:
    """Create Excel file with video data"""
    if not EXPORT_AVAILABLE:
        raise HTTPException(status_code=500, detail="Excel export not available. Install openpyxl.")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "YouTube Videos"
    
    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Headers
    headers = ["Title", "Channel", "Views", "Likes", "Comments", "URL", "Description"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Data rows
    for row, video in enumerate(videos, 2):
        ws.cell(row=row, column=1, value=video.title)
        ws.cell(row=row, column=2, value="YouTube")  # Default channel name
        ws.cell(row=row, column=3, value=video.views)
        ws.cell(row=row, column=4, value=video.likes)
        ws.cell(row=row, column=5, value=video.comment_count)
        ws.cell(row=row, column=6, value=video.video_url)
        ws.cell(row=row, column=7, value=video.description[:500])  # Limit description length
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

def create_pdf_file(videos: List[Video], keyword: str = "") -> bytes:
    """Create PDF file with video data"""
    if not EXPORT_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF export not available. Install reportlab.")
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    title_text = f"YouTube Video Search Results"
    if keyword:
        title_text += f" - {keyword}"
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    # Table data
    table_data = [["Title", "Views", "Likes", "Comments", "URL"]]
    
    for video in videos:
        # Truncate title if too long
        title = video.title[:50] + "..." if len(video.title) > 50 else video.title
        url = video.video_url[:30] + "..." if len(video.video_url) > 30 else video.video_url
        
        table_data.append([
            title,
            str(video.views),
            str(video.likes),
            str(video.comment_count),
            url
        ])
    
    # Create table
    table = Table(table_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch])
    
    # Table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])
    table.setStyle(table_style)
    
    story.append(table)
    doc.build(story)
    
    output.seek(0)
    return output.getvalue()

def extract_video_id(video_url: str) -> str:
    """Extract video ID from YouTube URL"""
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format")

def download_audio(video_url: str, output_dir: str) -> tuple[str, str, float]:
    """Download audio from YouTube video using yt-dlp"""
    try:
        video_id = extract_video_id(video_url)
        output_path = os.path.join(output_dir, f"{video_id}.%(ext)s")
        
        # yt-dlp command to extract audio only
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "m4a",
            "--audio-quality", "0",  # Best quality
            "--output", output_path,
            "--no-playlist",
            "--print", "title",
            "--print", "duration",
            "--print", "filename",
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Debug: print yt-dlp output
        logger.info(f"yt-dlp stdout:\n{result.stdout}")
        logger.info(f"yt-dlp stderr:\n{result.stderr}")
        logger.info(f"Files in temp dir after yt-dlp: {os.listdir(output_dir)}")
        
        if result.returncode != 0:
            raise Exception(f"yt-dlp failed: {result.stderr}")
        
        # Parse output to get title, duration, and filename
        output_lines = result.stdout.strip().split('\n')
        title = output_lines[0] if output_lines else "Unknown Title"
        duration = float(output_lines[1]) if len(output_lines) > 1 and output_lines[1].replace('.', '').isdigit() else 0.0
        filename = output_lines[2] if len(output_lines) > 2 else None
        
        # Find the downloaded audio file
        if filename and os.path.exists(filename):
            audio_file = filename
        else:
            # Try to find the file by video ID and common audio extensions
            for ext in ['m4a', 'mp3', 'wav', 'webm']:
                potential_file = os.path.join(output_dir, f"{video_id}.{ext}")
                if os.path.exists(potential_file):
                    audio_file = potential_file
                    break
            else:
                # Search for any file containing the video ID
                for file in os.listdir(output_dir):
                    if video_id in file and any(file.endswith(ext) for ext in ['.m4a', '.mp3', '.wav', '.webm']):
                        audio_file = os.path.join(output_dir, file)
                        break
                else:
                    # Last resort: find any audio file in the directory
                    for file in os.listdir(output_dir):
                        if any(file.endswith(ext) for ext in ['.m4a', '.mp3', '.wav', '.webm']):
                            audio_file = os.path.join(output_dir, file)
                            break
                    else:
                        raise Exception("Audio file not found after download")
        
        return audio_file, title, duration
        
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download audio: {str(e)}")

def transcribe_audio(audio_file: str) -> str:
    """Transcribe audio file using Whisper"""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=500, detail="Whisper model not available")
    
    try:
        logger.info(f"Transcribing audio file: {audio_file}")
        model = get_whisper_model()
        result = model.transcribe(audio_file)
        return result["text"].strip()
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

def chunk_text(text: str, max_length: int = 512) -> List[str]:
    """Split text into chunks for summarization"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_length and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_text(text: str) -> str:
    """Summarize text using transformer model or OpenAI API"""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=500, detail="Summarization model not available")
    
    try:
        # Handle empty or very short text
        if len(text.strip()) < 50:
            return text.strip()
        
        summarizer_model = get_summarizer()
        
        # Check if using OpenAI API
        if summarizer_model == "openai":
            return summarize_with_openai(text)
        
        # For very long text, chunk it and summarize each chunk
        if len(text) > 1024:
            chunks = chunk_text(text, 512)
            summaries = []
            
            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Only summarize chunks with substantial content
                    try:
                        result = summarizer_model(chunk, max_length=150, min_length=30, do_sample=False)
                        summaries.append(result[0]['summary_text'])
                    except Exception as e:
                        logger.warning(f"Failed to summarize chunk: {e}")
                        summaries.append(chunk[:200] + "...")  # Fallback to truncation
            
            # Combine summaries
            combined_summary = " ".join(summaries)
            
            # If combined summary is still too long, summarize it again
            if len(combined_summary) > 1024:
                try:
                    final_result = summarizer_model(combined_summary, max_length=300, min_length=100, do_sample=False)
                    return final_result[0]['summary_text']
                except:
                    return combined_summary[:500] + "..."  # Fallback
            
            return combined_summary
        else:
            # Direct summarization for shorter text
            result = summarizer_model(text, max_length=200, min_length=50, do_sample=False)
            return result[0]['summary_text']
            
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        # Fallback to simple truncation
        sentences = text.split('. ')
        if len(sentences) > 3:
            return '. '.join(sentences[:3]) + '.'
        return text[:500] + "..." if len(text) > 500 else text

def summarize_with_openai(text: str) -> str:
    """Summarize text using OpenAI API"""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise Exception("OpenAI API key not found")
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=openai_api_key)
        
        # For very long text, chunk it first
        if len(text) > 4000:
            chunks = chunk_text(text, 3000)
            summaries = []
            
            for chunk in chunks:
                if len(chunk.strip()) > 100:
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely and accurately."},
                                {"role": "user", "content": f"Please summarize the following text in 2-3 sentences:\n\n{chunk}"}
                            ],
                            max_tokens=150,
                            temperature=0.3
                        )
                        summaries.append(response.choices[0].message.content.strip())
                    except Exception as e:
                        logger.warning(f"Failed to summarize chunk with OpenAI: {e}")
                        summaries.append(chunk[:200] + "...")
            
            combined_summary = " ".join(summaries)
            
            # If still too long, summarize the combined summary
            if len(combined_summary) > 1000:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes text concisely and accurately."},
                        {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{combined_summary}"}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            
            return combined_summary
        else:
            # Direct summarization for shorter text
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text concisely and accurately."},
                    {"role": "user", "content": f"Please summarize the following text in 2-3 sentences:\n\n{text}"}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        logger.error(f"Error using OpenAI API: {e}")
        # Fallback to simple truncation
        sentences = text.split('. ')
        if len(sentences) > 3:
            return '. '.join(sentences[:3]) + '.'
        return text[:500] + "..." if len(text) > 500 else text

def create_transcript_pdf(transcription: str, summary: str, video_title: str, video_url: str) -> bytes:
    """Create PDF with transcription and summary"""
    if not EXPORT_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF export not available.")
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Title
    story.append(Paragraph("Video Transcription Report", title_style))
    story.append(Spacer(1, 12))
    
    # Video info
    story.append(Paragraph(f"<b>Video Title:</b> {video_title}", styles['Normal']))
    story.append(Paragraph(f"<b>Video URL:</b> {video_url}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Summary section
    story.append(Paragraph("Summary", heading_style))
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Full transcript section
    story.append(Paragraph("Full Transcription", heading_style))
    story.append(Paragraph(transcription, styles['Normal']))
    
    doc.build(story)
    output.seek(0)
    return output.getvalue()

def get_youtube_api_service():
    """Initialize YouTube API service"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API key not configured")
    
    try:
        return build("youtube", "v3", developerKey=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize YouTube API: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize YouTube API")

def search_videos_with_api(keyword: str) -> List[Video]:
    """Search videos using YouTube Data API v3"""
    try:
        youtube = get_youtube_api_service()
        
        # Calculate date for last 2 years
        two_years_ago = datetime.now() - timedelta(days=730)
        published_after = two_years_ago.isoformat() + "Z"
        
        # Search for videos
        search_response = youtube.search().list(
            q=keyword,
            part="id,snippet",
            maxResults=50,
            type="video",
            order="viewCount",
            publishedAfter=published_after
        ).execute()
        
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            return []
        
        # Get detailed video information
        videos_response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()
        
        videos = []
        for video_item in videos_response.get("items", []):
            snippet = video_item["snippet"]
            statistics = video_item["statistics"]
            
            # Get comments for this video
            comments = []
            try:
                comments_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_item["id"],
                    maxResults=5,
                    order="relevance"
                ).execute()
                
                for comment_item in comments_response.get("items", []):
                    comment_snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
                    comments.append(Comment(
                        text=comment_snippet["textDisplay"],
                        author=comment_snippet["authorDisplayName"],
                        likes=comment_snippet.get("likeCount", 0)
                    ))
            except Exception as e:
                logger.warning(f"Failed to fetch comments for video {video_item['id']}: {e}")
            
            videos.append(Video(
                title=snippet["title"],
                video_url=f"https://www.youtube.com/watch?v={video_item['id']}",
                views=int(statistics.get("viewCount", 0)),
                likes=int(statistics.get("likeCount", 0)),
                description=snippet["description"],
                comment_count=int(statistics.get("commentCount", 0)),
                top_comments=comments,
                thumbnail_url=snippet["thumbnails"]["high"]["url"]
            ))
        
        return videos
        
    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")

def search_videos_with_ytdlp(keyword: str) -> List[Video]:
    """Search videos using yt-dlp as fallback"""
    try:
        # Use yt-dlp to search YouTube
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--max-downloads", "50",
            "--playlist-items", "1-50",
            f"ytsearch50:{keyword}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            logger.error(f"yt-dlp error: {result.stderr}")
            raise Exception(f"yt-dlp failed: {result.stderr}")
        
        # Parse JSON output
        videos_data = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    videos_data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        videos = []
        for video_data in videos_data[:50]:  # Limit to 50 videos
            # Extract basic info
            title = video_data.get("title", "")
            video_url = video_data.get("webpage_url", "")
            views = video_data.get("view_count", 0)
            likes = video_data.get("like_count", 0)
            description = video_data.get("description", "")
            comment_count = video_data.get("comment_count", 0)
            thumbnail_url = video_data.get("thumbnail", "")
            
            # For yt-dlp, we can't easily get comments without additional requests
            # So we'll create empty comments
            comments = []
            
            videos.append(Video(
                title=title,
                video_url=video_url,
                views=views,
                likes=likes,
                description=description,
                comment_count=comment_count,
                top_comments=comments,
                thumbnail_url=thumbnail_url
            ))
        
        return videos
        
    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")

@app.post("/get_videos", response_model=VideoResponse)
async def get_videos(request: VideoRequest):
    """Get top 50 YouTube videos for a keyword"""
    try:
        videos = []
        source = "api"
        
        # Try YouTube API first
        try:
            videos = search_videos_with_api(request.keyword)
            logger.info(f"Successfully fetched {len(videos)} videos using YouTube API")
        except HTTPException as api_error:
            logger.warning(f"YouTube API failed, trying yt-dlp: {api_error}")
            # Fallback to yt-dlp
            try:
                videos = search_videos_with_ytdlp(request.keyword)
                source = "yt-dlp"
                logger.info(f"Successfully fetched {len(videos)} videos using yt-dlp")
            except HTTPException as ytdlp_error:
                logger.error(f"Both API and yt-dlp failed: {ytdlp_error}")
                raise ytdlp_error
        
        return VideoResponse(
            videos=videos,
            total_count=len(videos),
            source=source,
            keyword=request.keyword
        )
        
    except Exception as e:
        logger.error(f"Error in get_videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/excel")
async def export_to_excel(request: ExportRequest):
    """Export videos to Excel file"""
    try:
        if not request.videos:
            raise HTTPException(status_code=400, detail="No videos to export")
        
        # Get keyword from the first video's URL or use default
        keyword = "youtube_results"
        
        excel_data = create_excel_file(request.videos, keyword)
        filename = generate_filename("yt_results", "xlsx", keyword)
        
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export to Excel: {str(e)}")

@app.post("/export/pdf")
async def export_to_pdf(request: ExportRequest):
    """Export videos to PDF file"""
    try:
        if not request.videos:
            raise HTTPException(status_code=400, detail="No videos to export")
        
        # Get keyword from the first video's URL or use default
        keyword = "youtube_results"
        
        pdf_data = create_pdf_file(request.videos, keyword)
        filename = generate_filename("yt_results", "pdf", keyword)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export to PDF: {str(e)}")

@app.post("/transcribe/{video_url:path}", response_model=TranscribeResponse)
async def transcribe_video(video_url: str):
    """Transcribe a YouTube video"""
    try:
        if not AI_AVAILABLE:
            raise HTTPException(status_code=500, detail="AI libraries not available. Install whisper and transformers.")
        
        # Decode URL
        video_url = urllib.parse.unquote(video_url)
        
        # Validate YouTube URL
        if not ("youtube.com" in video_url or "youtu.be" in video_url):
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        logger.info(f"Starting transcription for video: {video_url}")
        
        # Create temporary directory for audio file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download audio
            logger.info("Downloading audio...")
            audio_file, video_title, duration = download_audio(video_url, temp_dir)
            
            # Transcribe audio
            logger.info("Transcribing audio...")
            transcription = transcribe_audio(audio_file)
            
            # Clean up temporary files
            try:
                os.remove(audio_file)
            except:
                pass
        
        logger.info(f"Transcription completed for: {video_title}")
        
        return TranscribeResponse(
            transcription=transcription,
            video_url=video_url,
            video_title=video_title,
            duration=duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to transcribe video: {str(e)}")

@app.post("/summarize_transcription", response_model=SummarizeResponse)
async def summarize_transcription(request: SummarizeRequest):
    """Summarize a transcription"""
    try:
        if not AI_AVAILABLE:
            raise HTTPException(status_code=500, detail="AI libraries not available. Install transformers.")
        
        if not request.transcription.strip():
            raise HTTPException(status_code=400, detail="Transcription text is empty")
        
        logger.info("Starting text summarization...")
        
        # Summarize the transcription
        summary = summarize_text(request.transcription)
        
        logger.info("Summarization completed")
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(request.transcription),
            summary_length=len(summary)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize transcription: {str(e)}")

@app.post("/export/transcript")
async def export_transcript(
    transcription: str,
    summary: str,
    video_title: str = "Unknown Video",
    video_url: str = "",
    format: str = "pdf"
):
    """Export transcription and summary as PDF or TXT"""
    try:
        if format.lower() == "pdf":
            # Create PDF
            pdf_data = create_transcript_pdf(transcription, summary, video_title, video_url)
            filename = generate_filename("transcript", "pdf", video_title)
            
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        elif format.lower() == "txt":
            # Create TXT content
            txt_content = f"Video Transcription Report\n"
            txt_content += f"{'=' * 50}\n\n"
            txt_content += f"Video Title: {video_title}\n"
            txt_content += f"Video URL: {video_url}\n\n"
            txt_content += f"SUMMARY\n"
            txt_content += f"{'-' * 20}\n"
            txt_content += f"{summary}\n\n"
            txt_content += f"FULL TRANSCRIPTION\n"
            txt_content += f"{'-' * 20}\n"
            txt_content += f"{transcription}\n"
            
            filename = generate_filename("transcript", "txt", video_title)
            
            return Response(
                content=txt_content.encode('utf-8'),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'pdf' or 'txt'")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting transcript: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export transcript: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ai_status = "available" if AI_AVAILABLE else "unavailable"
    export_status = "available" if EXPORT_AVAILABLE else "unavailable"
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ai_features": ai_status,
        "export_features": export_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 