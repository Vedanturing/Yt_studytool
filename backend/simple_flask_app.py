#!/usr/bin/env python3
"""
Simple Flask App with CORS
A simplified version of the Flask app with hardcoded CORS configuration
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple CORS configuration - allow all localhost ports
CORS(app, origins="*", supports_credentials=False)

print("✅ CORS configured with wildcard (*) for development")

# Study subjects data
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
    "315321-ADVANCE COMPUTER NETWORK": {
        "name": "Advanced Computer Network",
        "description": "Advanced networking concepts including OSI model, TCP/IP protocols, routing algorithms, and network security.",
        "units": {
            "Unit 1": ["Network Fundamentals", "OSI Model", "TCP/IP Protocol", "Network Topologies"],
            "Unit 2": ["Data Link Layer", "Error Detection", "Flow Control", "Medium Access Control"],
            "Unit 3": ["Network Layer", "Routing Algorithms", "IP Addressing", "Subnetting"],
            "Unit 4": ["Transport Layer", "TCP Protocol", "UDP Protocol", "Congestion Control"],
            "Unit 5": ["Application Layer", "HTTP/HTTPS", "DNS", "Network Security"]
        }
    },
    "315322-DATABASE MANAGEMENT SYSTEM": {
        "name": "Database Management System",
        "description": "Database design, SQL, normalization, and database administration concepts.",
        "units": {
            "Unit 1": ["Database Fundamentals", "Data Models", "ER Diagrams", "Database Design"],
            "Unit 2": ["Relational Model", "SQL Basics", "DDL Commands", "DML Commands"],
            "Unit 3": ["Normalization", "Functional Dependencies", "Normal Forms", "Database Design"],
            "Unit 4": ["Transaction Management", "ACID Properties", "Concurrency Control", "Recovery"],
            "Unit 5": ["Database Administration", "Security", "Backup", "Performance Tuning"]
        }
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "server": "Flask Simple App",
        "cors_enabled": True
    })

@app.route('/study/subjects', methods=['GET'])
def get_study_subjects():
    """Get available study subjects"""
    try:
        subjects = []
        for subject_code, subject_data in DIPLOMA_SUBJECTS.items():
            subjects.append({
                "code": subject_code,
                "name": subject_data["name"],
                "description": subject_data["description"],
                "unit_count": len(subject_data["units"])
            })
        
        response = jsonify({
            "subjects": subjects,
            "total_count": len(subjects)
        })
        
        # Add CORS headers manually for extra safety
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting study subjects: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study/subjects/<subject_code>/units', methods=['GET'])
def get_subject_units(subject_code):
    """Get units for a specific subject"""
    try:
        if subject_code not in DIPLOMA_SUBJECTS:
            return jsonify({"error": "Subject not found"}), 404
        
        subject_data = DIPLOMA_SUBJECTS[subject_code]
        units = []
        
        for unit_name, topics in subject_data["units"].items():
            units.append({
                "name": unit_name,
                "topics": topics,
                "topic_count": len(topics)
            })
        
        response = jsonify({
            "subject_code": subject_code,
            "subject_name": subject_data["name"],
            "units": units,
            "total_units": len(units)
        })
        
        # Add CORS headers manually for extra safety
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting subject units: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study/generate_material', methods=['POST'])
def generate_study_material():
    """Generate study material for selected units"""
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        units = data.get('units', [])
        
        if not subject or not units:
            return jsonify({"error": "Subject and units are required"}), 400
        
        # For now, return a simple response
        study_materials = {}
        for unit in units:
            study_materials[unit] = [
                {
                    "title": f"Study Guide for {unit}",
                    "type": "guide",
                    "url": f"https://example.com/study/{subject}/{unit}",
                    "description": f"Comprehensive study guide for {unit}"
                },
                {
                    "title": f"Practice Questions for {unit}",
                    "type": "quiz",
                    "url": f"https://example.com/quiz/{subject}/{unit}",
                    "description": f"Practice questions for {unit}"
                }
            ]
        
        response = jsonify({
            "subject": subject,
            "study_materials": study_materials
        })
        
        # Add CORS headers manually for extra safety
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating study material: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study/quiz/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz questions for selected units"""
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        units = data.get('units', [])
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        if not subject or not units:
            return jsonify({"error": "Subject and units are required"}), 400
        
        # Generate sample quiz questions
        questions = []
        for i in range(num_questions):
            unit = units[i % len(units)]
            questions.append({
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
        
        # Add CORS headers manually for extra safety
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/study/quiz/evaluate', methods=['POST'])
def evaluate_quiz():
    """Evaluate quiz responses"""
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        unit = data.get('unit', '')
        responses = data.get('responses', {})
        
        if not subject or not unit or not responses:
            return jsonify({"error": "Subject, unit, and responses are required"}), 400
        
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
        
        # Add CORS headers manually for extra safety
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Error evaluating quiz: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Flask Backend Server...")
    print("📖 API Documentation: http://localhost:8000/health")
    print("🔗 Health Check: http://localhost:8000/health")
    print("📚 Study Subjects: http://localhost:8000/study/subjects")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8000, debug=True) 