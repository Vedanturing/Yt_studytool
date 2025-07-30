#!/usr/bin/env python3
"""
CORS Fixed Flask App
A Flask app with the most permissive CORS configuration for development
"""

import os
import json
import logging
import uuid # Import the uuid module
from datetime import datetime
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# ReportLab imports for PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, ListFlowable, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents # Correct import for TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors # Import colors
from reportlab.pdfgen import canvas

# ReportLab Graphics imports for charts
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

import re

# Custom canvas for page numbers and footer
class _QuizReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page_num, page in enumerate(self.pages):
            self.__dict__.update(page)
            self.draw_page_footer(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_footer(self, page_num, num_pages):
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#555555')) # Gray color for footer
        self.drawString(inch, 0.75 * inch, f"Page {page_num} of {num_pages}")
        self.restoreState()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory store for quizzes (for demonstration purposes)
# In a production environment, you would use a proper database (e.g., SQLite, PostgreSQL)
quiz_store = {}

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

# Import web scraper and AI quiz generator
try:
    from web_scraper import StudyMaterialScraper
    from ai_quiz_generator import AIQuizGenerator
    from report_generator import ReportGenerator
    scraper = StudyMaterialScraper()
    quiz_generator = AIQuizGenerator()
    print("✅ Loaded web scraper and AI quiz generator")
except ImportError as e:
    print(f"⚠️  Could not import web scraper or AI quiz generator: {e}")
    scraper = None
    quiz_generator = None
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

# Helper function to generate a URL-friendly slug
def _generate_url_slug(text: str) -> str:
    text = text.lower()
    # Replace non-alphanumeric characters (except hyphens) with empty string
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')

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
        
        # Use web scraper to find real study materials
        study_materials = {}
        
        if scraper:
            logger.info(f"🔍 Using web scraper to find study materials for {subject}")
            for unit in units:
                # Get topics for this unit
                unit_topics = []
                if subject in DIPLOMA_SUBJECTS and unit in DIPLOMA_SUBJECTS[subject]["units"]:
                    unit_topics = DIPLOMA_SUBJECTS[subject]["units"][unit]
                
                # Search for real study materials
                materials = scraper.search_study_materials(subject, unit, unit_topics)
                study_materials[unit] = materials
                logger.info(f"✅ Found {len(materials.get('articles', []))} articles, {len(materials.get('videos', []))} videos, {len(materials.get('notes', []))} notes for {unit}")
        else:
            logger.warning("⚠️ Web scraper not available, using AI-powered fallback materials")
            # Use AI-powered fallback materials
            for unit in units:
                if scraper:
                    # Get topics for this unit
                    unit_topics = []
                    if subject in DIPLOMA_SUBJECTS and unit in DIPLOMA_SUBJECTS[subject]["units"]:
                        unit_topics = DIPLOMA_SUBJECTS[subject]["units"][unit]
                    
                    study_materials[unit] = scraper._get_gemini_fallback_materials(subject, unit, unit_topics)
                else:
                    study_materials[unit] = {
                    "articles": [
                        {
                            "title": f"Study Guide for {subject} - {unit}",
                            "url": f"https://www.geeksforgeeks.org/{subject.lower().replace(' ', '-')}/",
                            "description": f"Comprehensive study guide for {unit}",
                            "source": "GeeksforGeeks"
                        },
                        {
                            "title": f"Tutorial on {subject} - {unit}",
                            "url": f"https://www.tutorialspoint.com/{subject.lower().replace(' ', '_')}/",
                            "description": f"Step-by-step tutorial for {unit}",
                            "source": "TutorialsPoint"
                        }
                    ],
                    "videos": [
                        {
                            "title": f"Video Lecture: {subject} - {unit}",
                            "url": f"https://www.youtube.com/results?search_query={subject}+{unit}+tutorial",
                            "description": f"Video lecture on {unit}",
                            "source": "YouTube"
                        }
                    ],
                    "notes": [
                        {
                            "title": f"Lecture Notes for {subject} - {unit}",
                            "url": f"https://www.slideshare.net/search/slideshow?q={subject}+{unit}",
                            "description": f"Lecture notes and slides for {unit}",
                            "source": "SlideShare"
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
        
        # Use AI to generate real quiz questions
        questions = []
        
        if quiz_generator:
            logger.info(f"🤖 Using AI to generate quiz questions for {subject}")
            
            all_topics = []
            for unit in units:
                if subject in DIPLOMA_SUBJECTS and unit in DIPLOMA_SUBJECTS[subject]["units"]:
                    all_topics.extend(DIPLOMA_SUBJECTS[subject]["units"][unit])
            
            questions = quiz_generator.generate_quiz_questions(
                subject=subject,
                unit=", ".join(units),
                topics=all_topics,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            logger.info(f"✅ Generated {len(questions)} AI-powered questions")
        else:
            logger.warning("⚠️ AI quiz generator not available, using fallback questions")
            # Fallback to basic questions (as previously implemented)
            for i in range(num_questions):
                unit = units[i % len(units)]
                questions.append({
                    "id": i + 1,
                    "question": f"Sample question {i+1} for {unit}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "concept": f"Concept {i+1}",
                    "question_type": "mcq",
                    "difficulty": difficulty,
                    "explanation": f"This is the explanation for question {i+1}"
                })
        
        # Generate a unique quiz ID and store the quiz
        quiz_id = str(uuid.uuid4())
        quiz_store[quiz_id] = {
            "subject": subject,
            "units": units,
            "questions": questions,
            "total_questions": len(questions),
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"📝 Quiz stored with ID: {quiz_id}")

        response = jsonify({
            "quiz_id": quiz_id,
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
        quiz_id = data.get('quiz_id', '')
        subject = data.get('subject', '')
        unit = data.get('unit', '')
        responses = data.get('responses', {}) # Dictionary of {question_id: user_answer}
        
        if not quiz_id or not subject or not unit or not responses:
            error_response = jsonify({"error": "Quiz ID, subject, unit, and responses are required"}), 400
            return add_cors_headers(error_response[0]), error_response[1]
        
        # Retrieve the original quiz from storage
        stored_quiz = quiz_store.get(quiz_id)
        if not stored_quiz:
            error_response = jsonify({"error": "Quiz not found or expired"}), 404
            return add_cors_headers(error_response[0]), error_response[1]
        
        original_questions = stored_quiz["questions"]
        
        correct_count = 0
        total_questions = len(original_questions)
        mistakes = []
        
        # Create a map for quick lookup of original questions by ID
        original_questions_map = {q["id"]: q for q in original_questions}
        
        # Evaluate each response
        for question_id_str, user_answer in responses.items():
            # Convert question_id from string to int for lookup
            question_id = int(question_id_str)
            
            original_question = original_questions_map.get(question_id)
            
            if original_question:
                if user_answer == original_question["correct_answer"]:
                    correct_count += 1
                else:
                    # Retrieve study resources for the mistake's concept
                    # The study resources were already generated by web_scraper / Gemini fallback
                    # when generate_study_material was called. Here, we can provide general links
                    # or assume the frontend already has specific resources if needed.
                    # For now, we'll use a generic approach as before, but linked to the concept.

                    # The topic for study resources should be based on the concept of the incorrect question
                    concept_for_resources = original_question.get("concept", subject)

                    # Generate URL-friendly slugs
                    concept_slug = _generate_url_slug(concept_for_resources)
                    subject_slug = _generate_url_slug(subject)

                    # Attempt to create a more direct GeeksforGeeks URL
                    gfg_url = ""

                    if subject_slug == "operating-systems" and "system calls" in concept_for_resources.lower():
                        gfg_url = "https://www.geeksforgeeks.org/operating-systems/introduction-of-system-call/"
                    # Add more specific mappings here if needed for other subjects/concepts
                    elif subject_slug and concept_slug:
                        # Try pattern: /subject-slug/concept-slug/
                        gfg_url = f"https://www.geeksforgeeks.org/{subject_slug}/{concept_slug}/"
                    elif concept_slug: # If no clear subject slug, just use concept slug
                        gfg_url = f"https://www.geeksforgeeks.org/{concept_slug}/"
                    
                    # Fallback to search if direct URL is too generic or empty
                    if not gfg_url or len(gfg_url.split('/')) < 5: # Basic check for valid path depth
                        gfg_url = f"https://www.geeksforgeeks.org/search/?q={concept_for_resources.replace(' ', '+')}"

                    mistake = {
                        "concept": concept_for_resources,
                        "correct_answer": original_question["correct_answer"],
                        "user_answer": user_answer,
                        "question": original_question["question"],
                        "study_resources": [
                            {
                                "title": f"Study Guide: {concept_for_resources}",
                                "url": gfg_url, # Use the dynamically generated GfG URL
                                "type": "article",
                                "description": f"Comprehensive guide for {concept_for_resources} on GeeksforGeeks."
                            },
                            {
                                "title": f"Video Tutorial: {concept_for_resources}",
                                "url": f"https://www.youtube.com/results?search_query={concept_for_resources.replace(' ', '+')}+tutorial",
                                "type": "video",
                                "description": f"Video explanation of {concept_for_resources}"
                            },
                            {
                                "title": f"Practice Questions: {concept_for_resources}",
                                "url": f"https://www.tutorialspoint.com/search/search-results?search_string={concept_for_resources.replace(' ', '+')}+practice+questions",
                                "type": "practice",
                                "description": f"Practice questions for {concept_for_resources}"
                            }
                        ]
                    }
                    mistakes.append(mistake)
            else:
                logger.warning(f"Original question with ID {question_id} not found in stored quiz.")
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        if score >= 90:
            feedback = "Excellent work! You have a strong understanding of the material."
        elif score >= 70:
            feedback = "Good job! You understand most concepts, but there's room for improvement."
        elif score >= 50:
            feedback = "You're on the right track, but need more practice with these concepts."
        else:
            feedback = "Keep studying! Focus on the areas where you made mistakes."
        
        response = jsonify({
            "subject": subject,
            "unit": unit,
            "score": score,
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "feedback": feedback,
            "mistakes": mistakes,
            "original_questions": original_questions,
            "user_answers": responses
        })
        
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error evaluating quiz: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/generate_report', methods=['POST', 'OPTIONS'])
def generate_report():
    """Generate a study report"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)

    try:
        data = request.get_json()
        subject = data.get('subject', '')
        unit = data.get('unit', '')
        evaluation_result = data.get('evaluation_result', {})
        mistakes = evaluation_result.get('mistakes', []) # Ensure mistakes is always a list

        if not subject or not unit or not evaluation_result:
            error_response = jsonify({"error": "Subject, unit, and evaluation result are required"}), 400
            return add_cors_headers(error_response[0]), error_response[1]

        # Define the path for saving reports
        reports_dir = os.path.join(os.getcwd(), 'backend', 'storage', 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        # Generate the report using the ReportGenerator
        report_generator = ReportGenerator()
        logger.info(f"Generating report for subject: {subject}, unit: {unit}")
        report_filename = report_generator.generate_report_pdf(subject, unit, evaluation_result, reports_dir)
        logger.info(f"Generated report filename: {report_filename}")

        response = jsonify({
            "message": "Report generated successfully",
            "filename": report_filename,
            "report_url": f"/study/download_report/{report_filename}"
        })
        logger.info(f"Response being sent: {response.get_json()}")
        return add_cors_headers(response)

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        error_response = jsonify({"error": str(e)}), 500
        return add_cors_headers(error_response[0]), error_response[1]

@app.route('/study/download_report/<filename>', methods=['GET', 'OPTIONS'])
def download_report(filename):
    """Download a generated report file"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)

    try:
        reports_dir = os.path.join(os.getcwd(), 'backend', 'storage', 'reports')
        return send_from_directory(reports_dir, filename, as_attachment=True)
    except FileNotFoundError:
        error_response = jsonify({"error": "Report file not found"}), 404
        return add_cors_headers(error_response[0]), error_response[1]
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
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