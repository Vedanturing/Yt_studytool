# YouTube Video Search App

A modular UI-based program that fetches the top 15 YouTube videos from the past 2 years sorted by views, with a beautiful React frontend and Flask backend. Now with AI-powered transcription and summarization capabilities!

## Features

- **YouTube Data API v3 Integration**: Fetches top 15 videos from the past 2 years sorted by view count
- **yt-dlp Fallback**: Automatic fallback to yt-dlp scraper when API quota is exhausted
- **Detailed Video Information**: Includes views, likes, description, comments, and thumbnails
- **Modern React Frontend**: Built with TypeScript, TailwindCSS, and Zustand state management
- **Responsive Design**: Beautiful UI with error handling, loading states, and toast notifications
- **FastAPI/Flask Backend**: RESTful API with proper error handling and CORS support
- **Comprehensive Testing**: pytest-based unit tests for backend functionality
- **AI-Powered Transcription**: Download and transcribe video audio using OpenAI Whisper
- **Smart Summarization**: Summarize transcriptions using T5 models or OpenAI API
- **Export Functionality**: Export video data to Excel and PDF formats
- **Advanced Filtering**: Sort and filter videos by views, likes, publish date, and relevance

## Tech Stack

### Backend
- **Flask**: Web framework for the API
- **YouTube Data API v3**: Primary data source
- **yt-dlp**: Fallback scraper for when API quota is exhausted
- **OpenAI Whisper**: Audio transcription
- **Transformers (T5)**: Text summarization
- **OpenAI API**: Enhanced summarization (optional)
- **openpyxl**: Excel export functionality
- **reportlab**: PDF generation
- **pytest**: Unit testing framework
- **python-dotenv**: Environment variable management

### Frontend
- **React 18**: UI framework with TypeScript
- **TailwindCSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API requests
- **React Hot Toast**: Toast notifications

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- ffmpeg (required for video transcription)
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) and add to PATH
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
- YouTube Data API v3 key (optional, for full functionality)
- OpenAI API key (optional, for enhanced summarization)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd youtube-video-search
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your API keys (optional)
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application
```bash
# Terminal 1: Start backend
python start_backend.py

# Terminal 2: Start frontend
cd frontend
npm start
```

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## API Endpoints

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### POST /get_videos
Search for YouTube videos
```json
{
  "keyword": "python programming"
}
```

### POST /export/excel
Export video data to Excel format
```json
{
  "videos": [...]
}
```

### POST /export/pdf
Export video data to PDF format
```json
{
  "videos": [...]
}
```

### GET /transcribe/{video_url}
Transcribe video audio
```
GET /transcribe/https%3A//www.youtube.com/watch%3Fv%3Dexample
```

### POST /summarize_transcription
Summarize transcription text
```json
{
  "text": "transcription text here..."
}
```

## Configuration

### Environment Variables (.env)
```env
# Required for YouTube API functionality
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional: OpenAI API for enhanced summarization
OPENAI_API_KEY=your_openai_api_key_here

# Optional: AI model configuration
WHISPER_MODEL_SIZE=base  # tiny, base, small, medium, large
SUMMARIZATION_MODEL=t5-small  # t5-small, t5-base, t5-large, or openai
```

### API Key Setup

#### YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the key to your `.env` file

#### OpenAI API Key (Optional)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an API key
3. Add the key to your `.env` file
4. Set `SUMMARIZATION_MODEL=openai` to use OpenAI for summarization

## AI Features

### Transcription
- **OpenAI Whisper**: High-quality audio transcription
- **Configurable Models**: Choose from tiny, base, small, medium, or large models
- **Long Video Support**: Handles videos of any length with chunking
- **Multiple Formats**: Supports various audio formats

### Summarization
- **Local T5 Models**: Fast, offline summarization using transformer models
- **OpenAI API**: Enhanced summarization with GPT models (requires API key)
- **Smart Chunking**: Handles long texts by breaking them into manageable chunks
- **Fallback Mechanisms**: Graceful degradation if AI models fail

### Export Features
- **Excel Export**: Structured data export with timestamps
- **PDF Export**: Formatted reports with video information
- **Download Support**: Direct file downloads from the frontend

## Testing

### Backend Tests
```bash
python run_tests.py
```

### Manual API Testing
```bash
python test_api.py
```

## Project Structure

```
youtube-video-search/
├── backend/
│   ├── flask_app.py          # Flask backend application
│   ├── main.py              # FastAPI backend with AI features
│   └── simple_main.py       # Simplified FastAPI version
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Loader.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── VideoCard.tsx
│   │   │   ├── VideoList.tsx
│   │   │   ├── FilterControls.tsx
│   │   │   └── TranscriptionModal.tsx
│   │   ├── store/
│   │   │   └── useVideoStore.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tailwind.config.js
├── requirements.txt
├── package.json
├── setup.py
├── start_backend.py
├── run_tests.py
└── README.md
```

## Features in Detail

### Backend Features
- **YouTube Data API Integration**: Fetches top 15 videos from past 2 years
- **yt-dlp Fallback**: Automatic fallback when API quota is exhausted
- **Comment Fetching**: Retrieves top 5 comments per video (API only)
- **AI Transcription**: Download and transcribe video audio using Whisper
- **AI Summarization**: Summarize transcriptions using T5 or OpenAI
- **Export Functionality**: Excel and PDF export with timestamps
- **Error Handling**: Comprehensive error handling with fallback mechanisms
- **CORS Support**: Configured for React frontend
- **Health Check**: `/health` endpoint for monitoring

### Frontend Features
- **Search Interface**: Clean search bar with instant feedback
- **Video Cards**: Beautiful cards displaying video information
- **Filtering & Sorting**: Advanced controls for organizing video results
- **Transcription Modal**: Full-featured transcription interface
- **Export Buttons**: Easy access to Excel and PDF export
- **Loading States**: Skeleton loaders and spinners
- **Error Handling**: User-friendly error messages with retry options
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Toast Notifications**: Success and error notifications
- **State Management**: Zustand store for global state

### UI Components
- **SearchBar**: Search input with loading state
- **VideoCard**: Individual video display with metadata and transcription button
- **VideoList**: Grid layout for video results with filtering
- **FilterControls**: Advanced sorting and filtering options
- **TranscriptionModal**: Modal for transcription and summarization
- **Loader**: Skeleton and spinner loading components

## Troubleshooting

### Common Issues

1. **YouTube API Quota Exceeded**
   - The app will automatically fallback to yt-dlp
   - Check your API quota in Google Cloud Console

2. **yt-dlp Not Found**
   - Install yt-dlp: `pip install yt-dlp`
   - Or use: `pip install -r requirements.txt`

3. **CORS Errors**
   - Backend is configured for localhost:3000
   - Check that frontend is running on the correct port

4. **Port Already in Use**
   - Backend: Change port in `start_backend.py`
   - Frontend: Change port in `package.json` scripts

### Performance Tips
- YouTube API has daily quotas, use yt-dlp fallback when needed
- Consider caching results for frequently searched keywords
- Monitor API usage in Google Cloud Console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. 