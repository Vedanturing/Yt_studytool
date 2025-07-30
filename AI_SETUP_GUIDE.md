# 🤖 AI-Powered Study System Setup Guide

This guide will help you set up the AI-powered study material generation and quiz creation features.

## 🎯 Features Overview

### 🔍 Web Scraping for Study Materials
- **Real-time search** for articles, videos, and study materials
- **Educational websites** like GeeksforGeeks, TutorialsPoint, YouTube, SlideShare
- **Topic-based search** using your syllabus content
- **Fallback materials** if web scraping fails

### 🤖 AI-Powered Quiz Generation
- **Intelligent questions** based on your topics and concepts
- **Multiple AI providers** (OpenAI GPT, Google Gemini)
- **Context-aware** question generation
- **Fallback questions** if AI APIs are unavailable

## 🔑 API Key Setup

### 1. OpenAI API Key (Optional)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the API key
5. Add to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```

### 2. Google Gemini API Key (Recommended)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Add to your `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_key_here
   ```

## 🚀 How It Works

### Study Material Generation
When you click "Generate Study Materials":

1. **Topic Analysis**: System extracts topics from your selected units
2. **Web Search**: Searches educational websites for relevant content
3. **Content Categorization**: Organizes materials into articles, videos, and notes
4. **Real Links**: Provides actual URLs to study resources

**Example Search Queries:**
- "Operating System Process Management tutorial"
- "Memory Management study guide"
- "File Systems lecture notes"

### Quiz Generation
When you click "Generate Quiz":

1. **Topic Extraction**: Gets all topics from selected units
2. **AI Context**: Creates context for AI generation
3. **Question Generation**: AI creates intelligent questions
4. **Answer Validation**: Ensures questions have correct answers

**AI Prompt Example:**
```
Subject: Operating System
Unit: Unit 1
Topics: Process Management, Memory Management, File Systems

Generate 10 multiple choice questions that test understanding of these specific topics.
```

## 📊 Expected Results

### Study Materials Response
```json
{
  "study_materials": {
    "Unit 1": {
      "articles": [
        {
          "title": "Process Management Complete Guide",
          "url": "https://www.geeksforgeeks.org/process-management/",
          "description": "Comprehensive guide to process management",
          "source": "GeeksforGeeks"
        }
      ],
      "videos": [
        {
          "title": "Operating System Tutorial",
          "url": "https://youtube.com/watch?v=...",
          "description": "Video lecture on OS concepts",
          "source": "YouTube"
        }
      ],
      "notes": [
        {
          "title": "OS Lecture Notes",
          "url": "https://slideshare.net/...",
          "description": "Detailed lecture notes",
          "source": "SlideShare"
        }
      ]
    }
  }
}
```

### Quiz Questions Response
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is the primary purpose of process management?",
      "options": [
        "To allocate CPU time efficiently",
        "To manage file systems only",
        "To handle user interface",
        "To control network connections"
      ],
      "correct_answer": "To allocate CPU time efficiently",
      "concept": "Process Management",
      "explanation": "Process management is responsible for allocating CPU time..."
    }
  ]
}
```

## 🔧 Troubleshooting

### Web Scraper Issues
- **Network errors**: Normal in some environments, fallback materials will be used
- **Rate limiting**: System includes delays to be respectful
- **Empty results**: Check internet connection, fallback materials will be provided

### AI Generation Issues
- **API key missing**: System will use fallback questions
- **API errors**: Check API key validity and quotas
- **Model errors**: System will try alternative models

### Common Error Messages
```
❌ Failed to initialize OpenAI: Invalid API key
✅ Using fallback question generation

⚠️ Web scraper not available, using fallback materials
✅ Generated 10 fallback questions
```

## 🎯 Best Practices

### For Best Results:
1. **Set up both API keys** for maximum reliability
2. **Use specific unit selections** for targeted materials
3. **Check generated content** before sharing with students
4. **Monitor API usage** to avoid rate limits

### Performance Tips:
- **Gemini API** is generally faster and more reliable
- **Web scraping** works best with stable internet
- **Fallback modes** ensure the system always works

## 🔄 Testing Your Setup

Run the test script to verify everything is working:

```bash
python test_ai_functionality.py
```

Expected output:
```
🤖 Testing AI Functionality Setup
==================================================
OpenAI API Key: ✅ Set
Gemini API Key: ✅ Set
✅ Web scraper imported successfully
✅ AI quiz generator imported successfully

🔍 Testing Web Scraper...
✅ Web scraper test completed
   Found 3 articles
   Found 2 videos
   Found 1 notes

🤖 Testing AI Quiz Generator...
✅ AI quiz generator test completed
   Generated 3 questions

📝 Sample Question:
   Question: What is the primary purpose of process management?
   Options: ['To allocate CPU time efficiently', ...]
   Correct: To allocate CPU time efficiently
   Concept: Process Management
```

## 🎉 Success!

Once everything is set up, you'll have:
- ✅ **Real study materials** from educational websites
- ✅ **AI-generated quizzes** based on your syllabus
- ✅ **Detailed mistake analysis** with study recommendations
- ✅ **Fallback systems** for reliability

Your students will get a much more engaging and personalized learning experience! 