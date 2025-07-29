# Backend Server Setup

This project has two backend servers that can run on different ports:

## Option 1: Run Flask Server Only (Port 8000)
The Flask server includes basic video search functionality and study routes.

### Option 1a: Full Flask Server
```bash
cd backend
python flask_app.py
```

### Option 1b: Simple Flask Server (Recommended for CORS issues)
If you're experiencing CORS issues, try the simplified version:
```bash
cd backend
python simple_flask_app.py
```

This version has hardcoded CORS configuration and manual CORS headers for maximum compatibility.

This will start the Flask server on port 8000 with the following endpoints:
- `GET /health` - Health check
- `POST /get_videos` - Search YouTube videos
- `GET /study/subjects` - Get available study subjects
- `GET /study/subjects/{subject_code}/units` - Get units for a subject
- `POST /study/generate_material` - Generate study materials
- `POST /study/quiz/generate` - Generate quiz questions
- `POST /study/quiz/evaluate` - Evaluate quiz responses

## Option 2: Run FastAPI Server Only (Port 8001)
The FastAPI server includes advanced features like transcription, summarization, and learning mode.

```bash
cd backend
python main.py
```

This will start the FastAPI server on port 8001 with comprehensive API endpoints.

## Option 3: Run Both Servers (Recommended)
Use the dual server runner to start both servers simultaneously:

```bash
python run_backend_dual.py
```

This will start:
- Flask server on port 8000 (basic functionality)
- FastAPI server on port 8001 (advanced features)

## Frontend Configuration
The frontend is configured to connect to port 8000 by default. If you want to use the FastAPI server features, you may need to update the frontend configuration in:
- `frontend/src/components/Study.tsx`
- `frontend/src/components/OfflineManager.tsx`

Change the `API_BASE_URL` from `http://localhost:8000` to `http://localhost:8001` if you want to use the FastAPI server exclusively.

## API Documentation
- Flask API: http://localhost:8000/health
- FastAPI Documentation: http://localhost:8001/docs
- FastAPI Health Check: http://localhost:8001/health

## CORS Configuration
The backend servers are configured to allow requests from multiple localhost ports for development:
- `http://localhost:3000` (default React port)
- `http://localhost:3001` (alternative React port)
- `http://localhost:3002` through `http://localhost:3005` (additional development ports)

If you're running the frontend on a different port, the CORS configuration will automatically allow it.

## Testing CORS
To test if CORS is working correctly, run:
```bash
python test_cors.py
```

This will test both servers and verify that CORS headers are properly set.

## Troubleshooting
If you encounter port conflicts:
1. Make sure no other services are running on ports 8000 or 8001
2. Use `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac) to check port usage
3. Kill any processes using these ports before starting the servers

If you encounter CORS errors:
1. Make sure the backend servers are running
2. Check that your frontend is running on one of the allowed ports
3. Run the CORS test script to verify configuration
4. Restart the backend servers after making CORS changes 