# Enhanced Study Material Generation Guide

## Overview

The Stu-dih application now features an **Enhanced Study Material Generator** that combines multiple powerful technologies to provide comprehensive study resources:

- 🎥 **YouTube Video Scraping** using yt-dlp
- 🌐 **Web Scraping** for educational articles
- 📄 **Document Discovery** for PDFs, PPTs, and presentations
- 🤖 **AI-Powered Fallback** using Gemini AI

## Features

### 1. YouTube Video Integration (yt-dlp)

The enhanced generator uses `yt-dlp` to scrape real YouTube videos related to your study topics.

**What it provides:**
- Real YouTube video URLs with titles and descriptions
- Video metadata (duration, view count, uploader)
- Thumbnail images
- Direct download capability

**Example output:**
```json
{
  "title": "L-1.2: Batch Operating System | Types of Operating System",
  "url": "https://www.youtube.com/watch?v=povNcHSasgs",
  "description": "Video tutorial about Operating System concepts",
  "source": "YouTube",
  "duration": 432.0,
  "view_count": 1845282,
  "uploader": "Gate Smashers",
  "thumbnail": "https://..."
}
```

### 2. Web Scraping for Articles

Searches multiple educational websites for relevant articles and tutorials.

**Supported websites:**
- GeeksforGeeks
- TutorialsPoint
- Javatpoint
- W3Schools
- Stack Overflow
- Medium
- Dev.to
- FreeCodeCamp
- Khan Academy
- Coursera
- edX
- MIT OpenCourseWare

### 3. Document Discovery

Finds educational documents, presentations, and study materials.

**Document types:**
- PDF files
- PowerPoint presentations
- SlideShare presentations
- Academic papers (Academia.edu)
- Research papers (ResearchGate)
- Scribd documents

**Supported platforms:**
- SlideShare
- Academia.edu
- ResearchGate
- Scribd
- DocDroid
- Slides.com
- Prezi
- Canva

### 4. AI-Powered Fallback

When web scraping doesn't find enough materials, the system automatically falls back to:
1. **Enhanced Generator** (primary)
2. **Basic Web Scraping** (secondary)
3. **Gemini AI Generation** (tertiary)
4. **Static Fallback Materials** (final)

## API Endpoints

### Enhanced Study Material Generation

**Endpoint:** `POST /study/generate_enhanced_study_material`

**Request:**
```json
{
  "subject": "OPERATING SYSTEM",
  "units": ["Unit 1: Introduction to Operating Systems"]
}
```

**Response:**
```json
{
  "subject": "OPERATING SYSTEM",
  "study_materials": {
    "Unit 1: Introduction to Operating Systems": {
      "articles": [...],
      "videos": [...],
      "notes": [...]
    }
  },
  "generator_type": "enhanced"
}
```

### YouTube Video Download

**Endpoint:** `POST /study/download_youtube_video`

**Request:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=example"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video downloaded successfully",
  "video_info": {
    "title": "Video Title",
    "duration": 300,
    "uploader": "Channel Name",
    "view_count": 1000000
  },
  "download_path": "/storage/downloads/videos/video_title.mp4"
}
```

## Frontend Integration

### Enhanced Study Material Button

The frontend now uses the enhanced generator by default:

```typescript
const generateStudyMaterials = async () => {
  try {
    // Use enhanced endpoint first
    const response = await axios.post(`${API_BASE_URL}/study/generate_enhanced_study_material`, {
      subject: selectedSubject,
      units: selectedUnits
    });
    setStudyMaterials(response.data.study_materials);
    toast.success('Enhanced study materials generated successfully! 🚀');
  } catch (error) {
    // Fallback to basic generation
    const fallbackResponse = await axios.post(`${API_BASE_URL}/study/generate_study_material`, {
      subject: selectedSubject,
      units: selectedUnits
    });
    setStudyMaterials(fallbackResponse.data.study_materials);
    toast.success('Study materials generated successfully! (Basic mode)');
  }
};
```

### Video Download Feature

YouTube videos now include download buttons:

```typescript
const downloadYouTubeVideo = async (videoUrl: string, videoTitle: string) => {
  try {
    toast.info('Starting video download... This may take a few minutes.');
    
    const response = await axios.post(`${API_BASE_URL}/study/download_youtube_video`, {
      video_url: videoUrl
    });
    
    if (response.data.success) {
      toast.success(`Video "${videoTitle}" downloaded successfully!`);
    }
  } catch (error) {
    toast.error('Failed to download video. Please try again later.');
  }
};
```

### Enhanced Video Display

Videos now show additional metadata:

- Duration (formatted as MM:SS)
- View count (formatted with commas)
- Uploader name
- Download button for YouTube videos

## Installation and Setup

### Prerequisites

1. **Python Dependencies**
   ```bash
   pip install yt-dlp beautifulsoup4 requests
   ```

2. **yt-dlp Installation**
   ```bash
   pip install yt-dlp==2023.11.16
   ```

### Configuration

The enhanced generator is automatically initialized when the application starts. No additional configuration is required.

### Testing

Run the test script to verify everything works:

```bash
python test_enhanced_study_materials.py
```

Expected output:
```
🧪 Starting Enhanced Study Material Generator Tests
============================================================
🎥 Testing yt-dlp integration
✅ yt-dlp can extract video information
🌐 Testing web scraping functionality
✅ Web scraping is working
🚀 Testing Enhanced Study Material Generator
✅ Enhanced Study Material Generator initialized successfully
📊 Results:
   Articles: 0
   Videos: 6
   Notes: 0
✅ Enhanced Study Material Generator test completed successfully!
============================================================
📋 Test Summary:
   yt-dlp Integration: ✅ PASS
   Web Scraping: ✅ PASS
   Enhanced Generator: ✅ PASS
🎉 All tests passed! Enhanced Study Material Generator is ready to use.
```

## Usage Examples

### 1. Generate Study Materials for Operating Systems

1. Select "OPERATING SYSTEM" as the subject
2. Choose "Unit 1: Introduction to Operating Systems"
3. Click "Generate Study Materials"
4. The system will find:
   - YouTube videos from educational channels
   - Articles from GeeksforGeeks, TutorialsPoint, etc.
   - PDFs and presentations from SlideShare, Academia.edu

### 2. Download YouTube Videos

1. Generate study materials
2. Find a YouTube video in the results
3. Click the 📥 download button
4. The video will be downloaded to `/storage/downloads/videos/`

### 3. Access Different Content Types

- **Articles**: Click to open in new tab
- **Videos**: Click to watch on YouTube, or download locally
- **Notes**: Click to view PDFs, presentations, or academic papers

## Technical Details

### Architecture

```
Enhanced Study Material Generator
├── YouTube Video Scraping (yt-dlp)
├── Web Scraping (BeautifulSoup + Requests)
├── Document Discovery (Google Search + Site-specific scraping)
└── AI Fallback (Gemini AI)
```

### Parallel Processing

The generator uses `ThreadPoolExecutor` to run scraping tasks in parallel:

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    articles_future = executor.submit(self._scrape_articles, search_queries)
    videos_future = executor.submit(self._scrape_youtube_videos, search_queries)
    documents_future = executor.submit(self._scrape_documents, search_queries)
```

### Rate Limiting

The system includes respectful delays between requests:

```python
time.sleep(random.uniform(1, 2))  # 1-2 second delays
```

### Error Handling

Comprehensive error handling with multiple fallback levels:

1. Enhanced generator fails → Basic scraping
2. Basic scraping fails → Gemini AI
3. Gemini AI fails → Static materials

## Performance

### Typical Results

For a single unit, the enhanced generator typically finds:
- **6-8 articles** from educational websites
- **4-6 videos** from YouTube
- **4-6 documents** (PDFs, PPTs, presentations)

### Processing Time

- **Enhanced generation**: 30-60 seconds
- **Basic fallback**: 10-20 seconds
- **AI fallback**: 5-10 seconds

## Troubleshooting

### Common Issues

1. **No videos found**
   - Check internet connection
   - Verify yt-dlp is installed: `pip install yt-dlp`
   - Try different search terms

2. **No articles found**
   - Check if educational sites are accessible
   - Verify BeautifulSoup is installed: `pip install beautifulsoup4`

3. **Download fails**
   - Check available disk space
   - Verify write permissions to `/storage/downloads/videos/`
   - Try smaller videos first

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Offline Video Storage**
   - Cache downloaded videos
   - Index for quick search

2. **Content Filtering**
   - Quality scoring for videos
   - Relevance ranking

3. **Batch Downloads**
   - Download multiple videos at once
   - Progress tracking

4. **Content Summarization**
   - AI-powered summaries of articles
   - Video transcript extraction

### Contributing

To contribute to the enhanced study material generator:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues or questions about the enhanced study material generator:

1. Check the troubleshooting section
2. Run the test script to verify setup
3. Check the logs for error messages
4. Create an issue with detailed information

---

**Note**: The enhanced study material generator respects website terms of service and includes appropriate delays between requests to avoid overwhelming servers. 