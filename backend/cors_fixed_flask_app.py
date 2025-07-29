#!/usr/bin/env python3
"""
CORS Fixed Flask App
A Flask app with the most permissive CORS configuration for development
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Most permissive CORS configuration for development
CORS(app, 
     origins="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["*"],
     supports_credentials=False)

print("✅ CORS configured with maximum permissiveness for development")

# Import syllabus parser
try:
    from syllabus_parser import get_detailed_subjects
    DIPLOMA_SUBJECTS = get_detailed_subjects()
    print("✅ Loaded subjects from syllabus parser")
except ImportError as e:
    print(f"⚠️  Could not import syllabus parser: {e}")
    # Fallback to basic subjects
    DIPLOMA_SUBJECTS = {
        "315319-OPERATING SYSTEM": {
            "name": "Operating System",
            "description": "Comprehensive study of operating system concepts, process management, memory management, and system architecture.",
            "units": {
                "Unit 1": ["Introduction to Operating Systems", "OS Functions", "OS Types", "System Calls"],
                "Unit 2": ["Process Management", "Process States", "Process Scheduling", "Interprocess Communication"],
                "Unit 3": ["Memory Management", "Virtual Memory", "Page Replacement", "Memory Allocation"],
                "Unit 4": ["File Systems", "File Organization", "Directory Structure", "File Operations"],
                "Unit 5": ["Device Management", "I/O Systems", "Device Drivers", "Disk Scheduling"]
            }
        },
        "315323-SOFTWARE ENGINEERING": {
            "name": "Software Engineering",
            "description": "Software development methodologies, system analysis, design patterns, and project management principles.",
            "units": {
                "Unit 1": ["Introduction to Software Engineering", "Software Development Life Cycle", "Software Process Models", "Requirements Engineering"],
                "Unit 2": ["System Analysis and Design", "Object-Oriented Analysis", "UML Diagrams and Modeling", "Design Patterns"],
                "Unit 3": ["Software Testing", "Testing Strategies and Methods", "Unit Testing and Integration Testing", "System Testing and Validation"],
                "Unit 4": ["Software Quality Assurance", "Quality Metrics and Standards", "Code Review and Inspection", "Software Maintenance"],
                "Unit 5": ["Software Project Management", "Project Planning and Estimation", "Risk Management", "Team Management"]
            }
        },
        "315326-DATA ANALYTICS": {
            "name": "Data Analytics",
            "description": "Data analysis techniques, statistical methods, data visualization, and business intelligence concepts.",
            "units": {
                "Unit 1": ["Introduction to Data Analytics", "Types of Data and Data Sources", "Data Collection Methods", "Data Preprocessing"],
                "Unit 2": ["Statistical Analysis", "Descriptive Statistics", "Inferential Statistics", "Hypothesis Testing"],
                "Unit 3": ["Data Visualization", "Visualization Principles", "Charts and Graphs", "Interactive Dashboards"],
                "Unit 4": ["Machine Learning Basics", "Supervised Learning", "Unsupervised Learning", "Model Evaluation"],
                "Unit 5": ["Business Intelligence", "Data Warehousing", "OLAP and Data Cubes", "Business Analytics"]
            }
        }
    }

def add_cors_headers(response):
    """Add CORS headers to any response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'false'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    response = jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "server": "CORS Fixed Flask App",
        "cors_enabled": True,
        "message": "CORS is fully enabled for all origins"
    })
    return add_cors_headers(response)

@app.route('/study/subjects', methods=['GET', 'OPTIONS'])
def get_study_subjects():
    """Get available study subjects"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        return add_cors_headers(response)
    
    try:
        subjects = []
        for subject_code, subject_data in DIPLOMA_SUBJECTS.items():
            # Calculate total topics across all units
            total_topics = sum(len(topics) for topics in subject_data["units"].values())
            
            subjects.append({
                "code": subject_code,
                "name": subject_data["name"],
                "description": subject_data["description"],
                "units": list(subject_data["units"].keys()),  # Array of unit names
                "total_topics": total_topics,
                "difficulty": "Intermediate"  # Default difficulty
            })
        
        response = jsonify({
            "subjects": subjects,
            "total_count": len(subjects)
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error getting study subjects: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/subjects/<subject_code>/units', methods=['GET', 'OPTIONS'])
def get_subject_units(subject_code):
    """Get units for a specific subject"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        return add_cors_headers(response)
    
    try:
        if subject_code not in DIPLOMA_SUBJECTS:
            error_response = jsonify({"error": "Subject not found"}), 404
            return add_cors_headers(error_response[0]), error_response[1]
        
        subject_data = DIPLOMA_SUBJECTS[subject_code]
        units = []
        
        for unit_name, topics in subject_data["units"].items():
            units.append({
                "unit": unit_name,  # Changed from "name" to "unit" to match frontend
                "topics": topics
            })
        
        response = jsonify({
            "subject_code": subject_code,
            "subject_name": subject_data["name"],
            "units": units,
            "total_units": len(units)
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error getting subject units: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/generate_study_material', methods=['POST', 'OPTIONS'])
def generate_study_material():
    """Generate study material for selected units"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        return add_cors_headers(response)
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        units = data.get('units', [])
        
        if not subject or not units:
            error_response = jsonify({"error": "Subject and units are required"}), 400
            return add_cors_headers(error_response[0]), error_response[1]
        
        # Return study materials in the format expected by frontend
        study_materials = {}
        for unit in units:
            study_materials[unit] = {
                "articles": [
                    {
                        "title": f"Comprehensive Study Guide for {unit}",
                        "url": f"https://example.com/study/{subject}/{unit}",
                        "description": f"Detailed study guide covering all topics in {unit}",
                        "source": "StudyHub"
                    },
                    {
                        "title": f"Key Concepts Summary for {unit}",
                        "url": f"https://example.com/summary/{subject}/{unit}",
                        "description": f"Quick reference guide for {unit} concepts",
                        "source": "StudyHub"
                    }
                ],
                "videos": [
                    {
                        "title": f"Video Lecture: {unit} Overview",
                        "url": f"https://youtube.com/watch?v=lecture_{subject}_{unit}",
                        "description": f"Comprehensive video lecture on {unit}",
                        "source": "YouTube"
                    },
                    {
                        "title": f"Tutorial: {unit} Practical Examples",
                        "url": f"https://youtube.com/watch?v=tutorial_{subject}_{unit}",
                        "description": f"Practical examples and demonstrations for {unit}",
                        "source": "YouTube"
                    }
                ],
                "notes": [
                    {
                        "title": f"Lecture Notes for {unit}",
                        "url": f"https://example.com/notes/{subject}/{unit}",
                        "description": f"Detailed lecture notes for {unit}",
                        "source": "Course Materials"
                    },
                    {
                        "title": f"Practice Problems for {unit}",
                        "url": f"https://example.com/practice/{subject}/{unit}",
                        "description": f"Practice problems and solutions for {unit}",
                        "source": "Course Materials"
                    }
                ]
            }
        
        response = jsonify({
            "subject": subject,
            "study_materials": study_materials
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error generating study material: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/generate_quiz', methods=['POST', 'OPTIONS'])
def generate_quiz():
    """Generate quiz questions for selected units"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        return add_cors_headers(response)
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        units = data.get('units', [])
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        if not subject or not units:
            error_response = jsonify({"error": "Subject and units are required"}), 400
            return add_cors_headers(error_response[0]), error_response[1]
        
        # Generate sample quiz questions
        questions = []
        for i in range(num_questions):
            unit = units[i % len(units)]
            questions.append({
                "id": i + 1,  # Add ID field that frontend expects
                "question": f"Sample question {i+1} for {unit}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "concept": f"Concept {i+1}",
                "question_type": "mcq",
                "difficulty": difficulty,
                "explanation": f"This is the explanation for question {i+1}"
            })
        
        response = jsonify({
            "subject": subject,
            "questions": questions,
            "total_questions": len(questions),
            "difficulty": difficulty
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/evaluate_quiz', methods=['POST', 'OPTIONS'])
def evaluate_quiz():
    """Evaluate quiz responses"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        return add_cors_headers(response)
    
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        unit = data.get('unit', '')
        responses = data.get('responses', {})
        
        if not subject or not unit or not responses:
            error_response = jsonify({"error": "Subject, unit, and responses are required"}), 400
            return add_cors_headers(error_response[0]), error_response[1]
        
        # Simple evaluation logic
        correct_count = 0
        total_questions = len(responses)
        
        for question_id, answer in responses.items():
            # For demo purposes, assume all answers are correct
            correct_count += 1
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        response = jsonify({
            "subject": subject,
            "unit": unit,
            "score": score,
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "feedback": "Good job! Keep studying to improve your score."
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error evaluating quiz: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

if __name__ == '__main__':
    print("🚀 Starting CORS Fixed Flask Backend Server...")
    print("📖 API Documentation: http://localhost:8000/health")
    print("🔗 Health Check: http://localhost:8000/health")
    print("📚 Study Subjects: http://localhost:8000/study/subjects")
    print("✅ CORS is fully enabled for ALL origins")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8000, debug=True) 