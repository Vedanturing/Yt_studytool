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
- **📚 Syllabus-Based Learning**: Upload course syllabi (PDF/DOCX/text) and automatically find relevant videos
- **🧠 AI Quiz Generation**: Generate interactive quizzes based on syllabus topics using AI
- **📊 Learning Analytics**: Comprehensive reports with performance tracking and personalized recommendations
- **🎯 Smart Recommendations**: Get personalized study suggestions based on quiz performance and watched videos
- **💾 Offline-Capable Quiz Archiving**: Automatically save generated quizzes locally for offline access
- **📚 Study Material Caching**: Store and organize study materials (videos, notes, PDFs) locally
- **🔄 Intelligent Fallback System**: Graceful degradation when AI services are unavailable
- **📊 Enhanced Quiz Intelligence**: Support for difficulty levels, question types, and smart distractor generation
- **🎨 Modern Landing Page**: Beautiful, responsive landing page with animated sections and clear feature showcase
- **🎓 Unified Study Module**: Complete study flow for Diploma Computer Engineering 5th Sem students
- **📖 Auto-Generated Study Materials**: Web-scraped study resources with intelligent caching
- **🧪 Smart Quiz System**: AI-powered quiz generation with mistake analysis and concept mapping
- **📄 Comprehensive Reports**: Detailed PDF reports with performance analytics and personalized recommendations

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
- **PyPDF2**: PDF syllabus parsing
- **python-docx**: DOCX syllabus parsing
- **Google Gemini API**: AI-powered quiz generation and learning analytics

### Frontend
- **React 18**: UI framework with TypeScript
- **TailwindCSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API requests
- **React Hot Toast**: Toast notifications
- **Framer Motion**: Smooth animations and transitions
- **React Router**: Client-side routing for seamless navigation

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

## Landing Page Features

The new landing page includes:

### 🎨 Design Elements
- **Hero Section**: Bold introduction with animated background blobs and clear value proposition
- **How It Works**: 3-step process explanation with animated cards
- **Features Grid**: Comprehensive showcase of all app features with interactive cards
- **Call-to-Action**: Multiple CTAs throughout the page to encourage user engagement
- **Responsive Design**: Fully responsive across desktop, tablet, and mobile devices

### 🚀 Interactive Components
- **Animated Navigation**: Smooth navbar with mobile menu and theme toggle
- **Feature Cards**: Hover effects and smooth transitions for each feature
- **Scroll Animations**: Framer Motion animations that trigger on scroll
- **Gradient Backgrounds**: Beautiful gradient backgrounds with animated elements
- **Modern Footer**: Comprehensive footer with links and social information

### 📱 User Experience
- **Smooth Scrolling**: Seamless navigation between sections
- **Loading States**: Proper loading indicators for route transitions
- **Theme Support**: Dark/light mode toggle with persistent state
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Performance**: Optimized animations and lazy loading

### 🎯 Feature Showcase
The landing page highlights all core features:
1. **Syllabus Upload & Topic Extraction** - AI-powered syllabus parsing
2. **YouTube Video Curation** - Intelligent video recommendations
3. **Learning Mode with Flashcards** - Interactive learning tools
4. **Quiz Generator** - Customizable quizzes with offline support
5. **Performance Reports** - Detailed analytics and insights
6. **Study Playlist Creator** - Organized learning materials
7. **Material Downloader** - Offline access to content
8. **Settings & Customization** - Personalized experience

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

### POST /upload_syllabus
Upload and parse syllabus (file or text)
```
POST /upload_syllabus
Content-Type: multipart/form-data

file: [PDF/DOCX file] OR text_content: "syllabus text"
```

### POST /videos_by_syllabus
Get videos for syllabus topics
```json
{
  "topics": [
    {
      "unit": "Unit 1",
      "topic": "Introduction to AI",
      "description": "Basic concepts"
    }
  ]
}
```

### POST /generate_quiz
Generate quiz questions based on topics with offline support
```json
{
  "topics": ["Machine Learning", "Neural Networks"],
  "num_questions": 10,
  "question_types": ["mcq", "true_false"],
  "difficulty": "medium",
  "subject": "Computer Science"
}
```

### GET /available_quizzes
Get list of available offline quizzes
```
GET /available_quizzes?subject=Computer%20Science
```

### GET /load_quiz/{subject}/{unit}/{topic}
Load a specific quiz from offline storage
```
GET /load_quiz/Computer%20Science/Unit%201/Machine%20Learning
```

### POST /save_study_material
Save study material to local storage
```
POST /save_study_material
Content-Type: multipart/form-data

subject: "Computer Science"
topic: "Machine Learning"
material_type: "note"
title: "ML Basics Notes"
url: "https://example.com/ml-notes"
file: [optional PDF file]
```

### GET /get_study_materials/{subject}/{topic}
Get study materials for a specific topic
```
GET /get_study_materials/Computer%20Science/Machine%20Learning
```

### POST /generate_report
Generate learning report
```json
{
  "quiz_attempts": [
    {
      "question": "What is AI?",
      "selected_answer": "Artificial Intelligence",
      "correct_answer": "Artificial Intelligence",
      "is_correct": true,
      "topic": "AI Basics"
    }
  ],
  "watched_videos": ["https://youtube.com/watch?v=example"],
  "syllabus_topics": [...]
}
```

## Study Module API Endpoints

### GET /study/subjects
Get available subjects for Diploma Computer Engineering 5th Sem
```json
{
  "subjects": [
    {
      "code": "315319-OPERATING SYSTEM",
      "name": "Operating System",
      "units": ["Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5"]
    }
  ]
}
```

### GET /study/subjects/{subject_code}/units
Get units and topics for a specific subject
```json
{
  "subject_code": "315319-OPERATING SYSTEM",
  "subject_name": "Operating System",
  "units": [
    {
      "unit": "Unit 1",
      "topics": ["Introduction to Operating Systems", "OS Functions", "OS Types", "System Calls"]
    }
  ]
}
```

### POST /study/generate_study_material
Generate study material for selected units
```json
{
  "subject": "315319-OPERATING SYSTEM",
  "units": ["Unit 1", "Unit 2"]
}
```

### POST /study/generate_quiz
Generate quiz questions for selected units
```json
{
  "subject": "315319-OPERATING SYSTEM",
  "units": ["Unit 1"],
  "num_questions": 10,
  "difficulty": "medium",
  "question_types": ["mcq", "true_false"]
}
```

### POST /study/evaluate_quiz
Evaluate quiz responses and identify mistakes
```json
{
  "subject": "315319-OPERATING SYSTEM",
  "unit": "Unit 1",
  "responses": {
    "0": "Manage hardware resources",
    "1": "7"
  }
}
```

### POST /study/generate_report
Generate comprehensive PDF report
```json
{
  "subject": "315319-OPERATING SYSTEM",
  "unit": "Unit 1",
  "evaluation_result": {
    "score": 85.0,
    "correct_count": 8,
    "total_questions": 10,
    "mistakes": [...]
  }
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

### Syllabus-Based Learning Features
- **📚 Syllabus Upload**: Support for PDF, DOCX, and plain text syllabus uploads
- **🔍 Smart Parsing**: Automatic extraction of topics and units from syllabus content
- **📹 Video Mapping**: Find relevant YouTube videos for each syllabus topic
- **🧠 AI Quiz Generation**: Generate interactive quizzes using AI (Gemini/OpenAI)
- **📊 Learning Analytics**: Comprehensive performance tracking and analysis
- **💡 Smart Recommendations**: Personalized study suggestions based on performance
- **📈 Progress Tracking**: Monitor learning progress across topics and units

### Study Module Features
- **🎓 Subject & Unit Selection**: Pre-configured subjects for Diploma Computer Engineering 5th Sem
- **📖 Auto-Generated Study Materials**: Web-scraped articles, videos, and notes with intelligent caching
- **🧪 Smart Quiz System**: AI-powered quiz generation with difficulty levels and question types
- **🔍 Mistake Analysis**: Automatic identification of weak concepts and personalized study recommendations
- **📄 Comprehensive Reports**: Detailed PDF reports with performance analytics and improvement suggestions
- **💾 Intelligent Caching**: Offline storage for study materials and quizzes with fallback mechanisms
- **🎯 Progress Tracking**: Step-by-step progress tracking with visual indicators
- **📱 Responsive Design**: Mobile-first design with smooth animations and transitions

### Offline-Capable Features
- **💾 Quiz Archiving**: Automatically save generated quizzes to local storage for offline access
- **📚 Study Material Caching**: Store videos, notes, and PDFs locally organized by subject/topic
- **🔄 Intelligent Fallback**: When AI services fail, load from offline storage or use fallback questions
- **📊 Enhanced Quiz Intelligence**: Support for difficulty levels (easy/medium/hard) and question types (MCQ, True/False, Fill-in-the-blank, Code output)
- **🎯 Smart Distractor Generation**: AI-powered generation of plausible wrong answers
- **📱 Offline Manager**: Dedicated interface to manage and access offline content

## Testing

### Backend Tests
```bash
python run_tests.py
```

### Manual API Testing
```bash
python test_api.py
```

### Offline Functionality Testing
```bash
python test_offline_functionality.py
```

### Study Module Testing
```bash
python test_study_module.py
```

## Project Structure

```
youtube-video-search/
├── backend/
│   ├── flask_app.py          # Flask backend application
│   ├── main.py              # FastAPI backend with AI features
│   ├── simple_main.py       # Simplified FastAPI version
│   └── study_routes.py      # Study module API routes
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Loader.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── VideoCard.tsx
│   │   │   ├── VideoList.tsx
│   │   │   ├── FilterControls.tsx
│   │   │   ├── TranscriptionModal.tsx
│   │   │   ├── Quiz.tsx
│   │   │   ├── OfflineManager.tsx
│   │   │   ├── Report.tsx
│   │   │   ├── Study.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── FeaturesSection.tsx
│   │   │   ├── HowItWorksSection.tsx
│   │   │   ├── CTASection.tsx
│   │   │   └── FeatureCard.tsx
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── SyllabusPage.tsx
│   │   │   ├── QuizPage.tsx
│   │   │   ├── LearningModePage.tsx
│   │   │   └── StudyPage.tsx
│   │   ├── store/
│   │   │   └── useVideoStore.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tailwind.config.js
├── storage/                  # Offline storage directory
│   ├── quizzes/             # Stored quiz files
│   ├── materials/           # Study materials
│   ├── notes/               # User notes
│   ├── reports/             # Generated reports
│   ├── report_templates/    # Report templates
│   └── storage.db           # SQLite metadata database
├── requirements.txt
├── package.json
├── setup.py
├── start_backend.py
├── run_tests.py
├── test_offline_functionality.py
├── test_study_module.py
└── README.md
```

### Storage Structure

The offline system uses a hierarchical storage structure:

```
storage/
├── quizzes/
│   └── {subject}/
│       └── {unit}_{topic}_{timestamp}.json
├── materials/
│   └── {subject}/
│       └── {topic}/
│           └── {timestamp}_{filename}
├── notes/
│   └── {subject}/
│       └── {unit}/
│           └── {topic}/
├── reports/
│   └── {user_id}/
│       └── {subject}/
│           └── report_{timestamp}.pdf
└── storage.db               # SQLite database for metadata
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
- **Landing Page**: Modern, animated landing page with feature showcase
- **Routing**: Client-side routing with React Router
- **Theme Support**: Dark/light mode with persistent state

### UI Components
- **SearchBar**: Search input with loading state
- **VideoCard**: Individual video display with metadata and transcription button
- **VideoList**: Grid layout for video results with filtering
- **FilterControls**: Advanced sorting and filtering options
- **TranscriptionModal**: Modal for transcription and summarization
- **Loader**: Skeleton and spinner loading components
- **Navbar**: Responsive navigation with mobile menu
- **Footer**: Comprehensive footer with links and information
- **HeroSection**: Bold introduction with animations
- **FeaturesSection**: Interactive feature showcase
- **HowItWorksSection**: Step-by-step process explanation
- **CTASection**: Call-to-action sections
- **FeatureCard**: Reusable feature display component

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

5. **Landing Page Not Loading**
   - Ensure React Router is installed: `npm install react-router-dom`
   - Check browser console for any JavaScript errors
   - Verify all component imports are correct

### Performance Tips
- YouTube API has daily quotas, use yt-dlp fallback when needed
- Consider caching results for frequently searched keywords
- Monitor API usage in Google Cloud Console
- Use production builds for better performance: `npm run build`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. 