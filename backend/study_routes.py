import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import requests
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("Warning: BeautifulSoup not available for web scraping.")
import re
from pathlib import Path

# Import existing AI libraries if available
try:
    import google.generativeai as genai
    from transformers.pipelines import pipeline
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: AI libraries not available for study module.")

# Import syllabus parser with robust import handling
SYLLABUS_PARSER_AVAILABLE = False
get_detailed_subjects = None
get_subject_summary = None

try:
    # Try relative import first (when running as module)
    from .syllabus_parser import get_detailed_subjects, get_subject_summary
    SYLLABUS_PARSER_AVAILABLE = True
    print("✅ Syllabus parser imported successfully (relative import)")
except ImportError:
    try:
        # Try absolute import (when running directly)
        from syllabus_parser import get_detailed_subjects, get_subject_summary
        SYLLABUS_PARSER_AVAILABLE = True
        print("✅ Syllabus parser imported successfully (absolute import)")
    except ImportError:
        try:
            # Try with backend prefix (when running from project root)
            from backend.syllabus_parser import get_detailed_subjects, get_subject_summary
            SYLLABUS_PARSER_AVAILABLE = True
            print("✅ Syllabus parser imported successfully (backend prefix)")
        except ImportError as e:
            SYLLABUS_PARSER_AVAILABLE = False
            print(f"⚠️  Syllabus parser not available: {e}")
            print("   Using default subjects instead.")

# Import PDF generation libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PDF libraries not available for report generation.")

router = APIRouter(prefix="/study", tags=["study"])

# Configure logging
logger = logging.getLogger(__name__)

# Create storage directories
STORAGE_DIR = Path("storage")
QUIZZES_DIR = STORAGE_DIR / "quizzes"
MATERIAL_CACHE_DIR = STORAGE_DIR / "material_cache"
REPORTS_DIR = STORAGE_DIR / "reports"

for dir_path in [QUIZZES_DIR, MATERIAL_CACHE_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Pydantic models
class SubjectUnit(BaseModel):
    subject: str
    unit: str
    topics: List[str]

class StudyMaterialRequest(BaseModel):
    subject: str
    units: List[str]

class QuizRequest(BaseModel):
    subject: str
    units: List[str]
    num_questions: int = 10
    difficulty: str = "medium"  # "easy", "medium", "hard"
    question_types: List[str] = ["mcq", "true_false", "fill_blank", "code_output"]
    user_id: str = "default"  # For report organization

class QuizResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    concept: str
    question_type: str
    difficulty: str
    explanation: str = ""

class QuizSubmission(BaseModel):
    subject: str
    unit: str
    responses: Dict[int, str]  # question_index: selected_answer
    user_id: str = "default"
    time_taken: int = 0  # Time in seconds

class MistakeAnalysis(BaseModel):
    concept: str
    correct_answer: str
    user_answer: str
    mistake_category: str  # "conceptual_confusion", "skipped", "careless_error"
    study_resources: List[Dict[str, str]]
    topic_accuracy: float = 0.0

class ReportRequest(BaseModel):
    subject: str
    unit: str
    evaluation_result: dict
    user_id: str = "default"
    report_style: str = "default"  # "default", "detailed", "summary"

class TopicAccuracy(BaseModel):
    topic: str
    accuracy: float
    questions_attempted: int
    total_questions: int
    mistakes: List[dict]

# Get detailed subjects from syllabus parser or use defaults
if SYLLABUS_PARSER_AVAILABLE and get_detailed_subjects is not None:
    DIPLOMA_SUBJECTS = get_detailed_subjects()
else:
    # Fallback to default subjects
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
                "Unit 5": ["Application Layer", "HTTP Protocol", "DNS", "Email Protocols"]
            }
        },
        "315323-SOFTWARE ENGINEERING": {
            "name": "Software Engineering",
            "description": "Software development methodologies, system analysis, design patterns, and project management principles.",
            "units": {
                "Unit 1": ["Software Engineering Introduction", "Software Process Models", "Software Life Cycle", "Requirements Engineering"],
                "Unit 2": ["System Analysis", "Data Flow Diagrams", "Entity Relationship Diagrams", "System Design"],
                "Unit 3": ["Object-Oriented Analysis", "UML Diagrams", "Class Diagrams", "Use Case Diagrams"],
                "Unit 4": ["Software Testing", "Testing Strategies", "Unit Testing", "Integration Testing"],
                "Unit 5": ["Software Maintenance", "Software Quality", "Software Metrics", "Project Management"]
            }
        }
    }

@router.get("/subjects")
async def get_subjects():
    """Get available subjects for Diploma Computer Engineering 5th Sem"""
    subjects = []
    
    for code, data in DIPLOMA_SUBJECTS.items():
        subject_info = {
            "code": code,
            "name": data["name"],
            "description": data.get("description", ""),
            "units": list(data["units"].keys()),
            "total_topics": sum(len(topics) for topics in data["units"].values())
        }
        
        # Add subject summary if available
        if SYLLABUS_PARSER_AVAILABLE and get_subject_summary is not None:
            summary = get_subject_summary(code)
            subject_info.update(summary)
        
        subjects.append(subject_info)
    
    return {"subjects": subjects}

@router.get("/subjects/{subject_code}/units")
async def get_subject_units(subject_code: str):
    """Get units and topics for a specific subject"""
    if subject_code not in DIPLOMA_SUBJECTS:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    subject_data = DIPLOMA_SUBJECTS[subject_code]
    return {
        "subject_code": subject_code,
        "subject_name": subject_data["name"],
        "units": [
            {
                "unit": unit,
                "topics": topics
            }
            for unit, topics in subject_data["units"].items()
        ]
    }

@router.post("/generate_study_material")
async def generate_study_material(request: StudyMaterialRequest):
    """Generate study material for selected units"""
    try:
        study_materials = {}
        
        for unit in request.units:
            # Check cache first
            cache_file = MATERIAL_CACHE_DIR / request.subject / f"{unit.replace(' ', '_')}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    study_materials[unit] = json.load(f)
                logger.info(f"Loaded cached study material for {unit}")
                continue
            
            # Generate new study material
            unit_materials = await _scrape_study_materials(request.subject, unit)
            
            # Cache the results
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(unit_materials, f, indent=2, ensure_ascii=False)
            
            study_materials[unit] = unit_materials
        
        return {
            "subject": request.subject,
            "units": request.units,
            "study_materials": study_materials
        }
        
    except Exception as e:
        logger.error(f"Error generating study material: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate study material: {str(e)}")

async def _scrape_study_materials(subject: str, unit: str) -> Dict[str, List[Dict[str, str]]]:
    """Scrape study materials from web sources"""
    materials = {
        "articles": [],
        "videos": [],
        "notes": []
    }
    
    # Search queries for different content types
    search_queries = [
        f"{subject} {unit} study notes",
        f"{subject} {unit} tutorial",
        f"{subject} {unit} lecture notes"
    ]
    
    for query in search_queries:
        try:
            # Simulate web scraping (in production, use proper web scraping)
            # For now, return mock data
            materials["articles"].append({
                "title": f"{unit} - Comprehensive Guide",
                "url": f"https://example.com/{unit.lower().replace(' ', '-')}",
                "description": f"Detailed study material for {unit}",
                "source": "StudyHub"
            })
            
            materials["videos"].append({
                "title": f"{unit} - Video Tutorial",
                "url": f"https://youtube.com/watch?v={unit.lower().replace(' ', '')}",
                "description": f"Video explanation of {unit} concepts",
                "source": "YouTube"
            })
            
            materials["notes"].append({
                "title": f"{unit} - Quick Notes",
                "url": f"https://notes.com/{unit.lower().replace(' ', '-')}",
                "description": f"Concise notes for {unit}",
                "source": "NotesApp"
            })
            
        except Exception as e:
            logger.warning(f"Failed to scrape materials for query '{query}': {e}")
            continue
    
    return materials

@router.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    """Generate unique quiz questions for selected units"""
    try:
        quiz_questions = []
        total_requested = request.num_questions
        units_count = len(request.units)
        
        # Calculate questions per unit (distribute evenly)
        questions_per_unit = total_requested // units_count
        remaining_questions = total_requested % units_count
        
        logger.info(f"Generating {total_requested} questions across {units_count} units")
        
        for i, unit in enumerate(request.units):
            # Calculate questions for this unit
            unit_question_count = questions_per_unit + (1 if i < remaining_questions else 0)
            
            # Check cache first
            cache_file = QUIZZES_DIR / request.subject / f"{unit.replace(' ', '_')}.json"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_questions = json.load(f)
                    # Randomly select from cached questions to ensure variety
                    import random
                    if len(cached_questions) >= unit_question_count:
                        selected_questions = random.sample(cached_questions, unit_question_count)
                    else:
                        selected_questions = cached_questions
                    quiz_questions.extend(selected_questions)
                logger.info(f"Loaded {len(selected_questions)} cached questions for {unit}")
                continue
            
            # Generate new quiz questions
            unit_questions = await _generate_quiz_questions(
                request.subject, 
                unit, 
                unit_question_count, 
                request.difficulty, 
                request.question_types
            )
            
            # Cache the results
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(unit_questions, f, indent=2, ensure_ascii=False)
            
            quiz_questions.extend(unit_questions)
        
        # Ensure uniqueness across all questions
        unique_questions = []
        seen_questions = set()
        
        for question in quiz_questions:
            question_key = f"{question['question']}_{question['correct_answer']}"
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_questions.append(question)
        
        # If we don't have enough unique questions, add more from available pool
        if len(unique_questions) < total_requested:
            logger.warning(f"Only {len(unique_questions)} unique questions available, requested {total_requested}")
        
        # Limit to requested number
        final_questions = unique_questions[:total_requested]
        
        logger.info(f"Generated {len(final_questions)} unique questions for {request.subject}")
        
        return {
            "subject": request.subject,
            "units": request.units,
            "questions": final_questions,
            "total_questions": len(final_questions),
            "questions_per_unit": questions_per_unit,
            "unique_questions": len(final_questions) == len(unique_questions)
        }
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

async def _generate_quiz_questions(subject: str, unit: str, num_questions: int, difficulty: str, question_types: List[str]) -> List[Dict]:
    """Generate unique quiz questions using AI or fallback to predefined questions"""
    questions = []
    
    if AI_AVAILABLE:
        try:
            # Use AI to generate questions (implement with Gemini/OpenAI)
            # For now, return fallback questions
            pass
        except Exception as e:
            logger.warning(f"AI quiz generation failed, using fallback: {e}")
    
    # Get comprehensive fallback questions based on subject and unit
    fallback_questions = _get_fallback_questions(subject, unit)
    
    # Ensure we have enough questions
    if len(fallback_questions) < num_questions:
        logger.warning(f"Not enough questions available for {subject} - {unit}. Available: {len(fallback_questions)}, Requested: {num_questions}")
        # Use all available questions
        num_questions = len(fallback_questions)
    
    # Randomly select questions to ensure uniqueness and variety
    import random
    selected_questions = random.sample(fallback_questions, num_questions)
    
    for i, question_data in enumerate(selected_questions):
        questions.append({
            "id": i,
            "question": question_data["question"],
            "options": question_data["options"],
            "correct_answer": question_data["correct_answer"],
            "concept": question_data["concept"],
            "question_type": question_data["type"],
            "difficulty": difficulty
        })
    
    logger.info(f"Generated {len(questions)} unique questions for {subject} - {unit}")
    return questions

def _get_fallback_questions(subject: str, unit: str) -> List[Dict]:
    """Get comprehensive fallback questions for when AI is not available"""
    fallback_db = {
        "315319-OPERATING SYSTEM": {
            "Unit 1": [
                {
                    "question": "What is the primary function of an operating system?",
                    "options": ["Run applications", "Manage hardware resources", "Connect to internet", "Create files"],
                    "correct_answer": "Manage hardware resources",
                    "concept": "OS Functions",
                    "type": "mcq"
                },
                {
                    "question": "Which of the following is NOT a type of operating system?",
                    "options": ["Batch OS", "Time-sharing OS", "Real-time OS", "Web OS"],
                    "correct_answer": "Web OS",
                    "concept": "OS Types",
                    "type": "mcq"
                },
                {
                    "question": "What is a system call in operating systems?",
                    "options": ["A function call", "A request to the kernel", "A hardware interrupt", "A user program"],
                    "correct_answer": "A request to the kernel",
                    "concept": "System Calls",
                    "type": "mcq"
                },
                {
                    "question": "Which component manages memory allocation in an OS?",
                    "options": ["CPU Scheduler", "Memory Manager", "File Manager", "Device Manager"],
                    "correct_answer": "Memory Manager",
                    "concept": "OS Functions",
                    "type": "mcq"
                },
                {
                    "question": "What is the main purpose of a device driver?",
                    "options": ["To run applications", "To manage hardware devices", "To create files", "To connect to network"],
                    "correct_answer": "To manage hardware devices",
                    "concept": "Device Management",
                    "type": "mcq"
                },
                {
                    "question": "Which OS type is designed for real-time applications?",
                    "options": ["Batch OS", "Time-sharing OS", "Real-time OS", "Distributed OS"],
                    "correct_answer": "Real-time OS",
                    "concept": "OS Types",
                    "type": "mcq"
                },
                {
                    "question": "What is the kernel in an operating system?",
                    "options": ["A user program", "The core component", "A device driver", "A file system"],
                    "correct_answer": "The core component",
                    "concept": "OS Architecture",
                    "type": "mcq"
                },
                {
                    "question": "Which OS function handles file operations?",
                    "options": ["Process Management", "Memory Management", "File Management", "Device Management"],
                    "correct_answer": "File Management",
                    "concept": "OS Functions",
                    "type": "mcq"
                },
                {
                    "question": "What is multiprogramming in OS?",
                    "options": ["Running multiple programs", "Multiple CPUs", "Multiple users", "Multiple files"],
                    "correct_answer": "Running multiple programs",
                    "concept": "OS Concepts",
                    "type": "mcq"
                },
                {
                    "question": "Which OS type allows multiple users to share resources?",
                    "options": ["Batch OS", "Time-sharing OS", "Real-time OS", "Single-user OS"],
                    "correct_answer": "Time-sharing OS",
                    "concept": "OS Types",
                    "type": "mcq"
                }
            ],
            "Unit 2": [
                {
                    "question": "What is a process in operating system?",
                    "options": ["A program in execution", "A file on disk", "A memory location", "A CPU register"],
                    "correct_answer": "A program in execution",
                    "concept": "Process Management",
                    "type": "mcq"
                },
                {
                    "question": "Which scheduling algorithm provides the shortest average waiting time?",
                    "options": ["FCFS", "SJF", "Round Robin", "Priority"],
                    "correct_answer": "SJF",
                    "concept": "Process Scheduling",
                    "type": "mcq"
                },
                {
                    "question": "What is the state of a process when it's waiting for I/O?",
                    "options": ["Running", "Ready", "Blocked", "Terminated"],
                    "correct_answer": "Blocked",
                    "concept": "Process States",
                    "type": "mcq"
                },
                {
                    "question": "What is context switching?",
                    "options": ["Changing programs", "Saving and loading process state", "Switching users", "Changing files"],
                    "correct_answer": "Saving and loading process state",
                    "concept": "Process Management",
                    "type": "mcq"
                },
                {
                    "question": "Which process state means the process is ready to execute?",
                    "options": ["New", "Ready", "Running", "Blocked"],
                    "correct_answer": "Ready",
                    "concept": "Process States",
                    "type": "mcq"
                },
                {
                    "question": "What is a thread in operating systems?",
                    "options": ["A lightweight process", "A file", "A memory location", "A device"],
                    "correct_answer": "A lightweight process",
                    "concept": "Threading",
                    "type": "mcq"
                },
                {
                    "question": "Which scheduling algorithm is preemptive?",
                    "options": ["FCFS", "SJF", "Round Robin", "All of the above"],
                    "correct_answer": "Round Robin",
                    "concept": "Process Scheduling",
                    "type": "mcq"
                },
                {
                    "question": "What is interprocess communication?",
                    "options": ["Processes talking to each other", "File sharing", "Memory sharing", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "IPC",
                    "type": "mcq"
                },
                {
                    "question": "What is a deadlock?",
                    "options": ["Process termination", "Resource sharing", "Processes waiting for each other", "Memory allocation"],
                    "correct_answer": "Processes waiting for each other",
                    "concept": "Deadlock",
                    "type": "mcq"
                },
                {
                    "question": "Which algorithm prevents deadlock?",
                    "options": ["Banker's Algorithm", "FCFS", "SJF", "Round Robin"],
                    "correct_answer": "Banker's Algorithm",
                    "concept": "Deadlock Prevention",
                    "type": "mcq"
                }
            ],
            "Unit 3": [
                {
                    "question": "What is virtual memory?",
                    "options": ["Physical RAM", "Storage on hard disk", "Memory management technique", "Cache memory"],
                    "correct_answer": "Memory management technique",
                    "concept": "Virtual Memory",
                    "type": "mcq"
                },
                {
                    "question": "Which page replacement algorithm replaces the least recently used page?",
                    "options": ["FIFO", "LRU", "Optimal", "Random"],
                    "correct_answer": "LRU",
                    "concept": "Page Replacement",
                    "type": "mcq"
                },
                {
                    "question": "What is paging in memory management?",
                    "options": ["Dividing memory into fixed-size blocks", "Allocating memory", "Freeing memory", "Swapping memory"],
                    "correct_answer": "Dividing memory into fixed-size blocks",
                    "concept": "Paging",
                    "type": "mcq"
                },
                {
                    "question": "What is a page fault?",
                    "options": ["Page corruption", "Page not in memory", "Page overflow", "Page deletion"],
                    "correct_answer": "Page not in memory",
                    "concept": "Page Faults",
                    "type": "mcq"
                },
                {
                    "question": "Which memory allocation technique suffers from external fragmentation?",
                    "options": ["Paging", "Segmentation", "Fixed partitioning", "Dynamic partitioning"],
                    "correct_answer": "Dynamic partitioning",
                    "concept": "Memory Allocation",
                    "type": "mcq"
                }
            ],
            "Unit 4": [
                {
                    "question": "What is a file system?",
                    "options": ["A program", "A method for storing files", "A device", "A network"],
                    "correct_answer": "A method for storing files",
                    "concept": "File Systems",
                    "type": "mcq"
                },
                {
                    "question": "Which file system is used by Windows?",
                    "options": ["ext4", "NTFS", "FAT32", "Both B and C"],
                    "correct_answer": "Both B and C",
                    "concept": "File Systems",
                    "type": "mcq"
                },
                {
                    "question": "What is a directory in file systems?",
                    "options": ["A file", "A container for files", "A device", "A program"],
                    "correct_answer": "A container for files",
                    "concept": "File Organization",
                    "type": "mcq"
                }
            ],
            "Unit 5": [
                {
                    "question": "What is device management in OS?",
                    "options": ["Managing hardware devices", "Managing files", "Managing memory", "Managing processes"],
                    "correct_answer": "Managing hardware devices",
                    "concept": "Device Management",
                    "type": "mcq"
                },
                {
                    "question": "Which scheduling algorithm is used for disk I/O?",
                    "options": ["FCFS", "SSTF", "SCAN", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "Disk Scheduling",
                    "type": "mcq"
                }
            ]
        },
        "315321-ADVANCE COMPUTER NETWORK": {
            "Unit 1": [
                {
                    "question": "How many layers are there in the OSI model?",
                    "options": ["5", "6", "7", "8"],
                    "correct_answer": "7",
                    "concept": "OSI Model",
                    "type": "mcq"
                },
                {
                    "question": "Which layer of OSI model handles routing?",
                    "options": ["Data Link", "Network", "Transport", "Application"],
                    "correct_answer": "Network",
                    "concept": "OSI Model",
                    "type": "mcq"
                },
                {
                    "question": "What is the main protocol of the Internet?",
                    "options": ["HTTP", "FTP", "TCP/IP", "SMTP"],
                    "correct_answer": "TCP/IP",
                    "concept": "TCP/IP Protocol",
                    "type": "mcq"
                },
                {
                    "question": "Which network topology is most reliable?",
                    "options": ["Bus", "Star", "Ring", "Mesh"],
                    "correct_answer": "Mesh",
                    "concept": "Network Topologies",
                    "type": "mcq"
                },
                {
                    "question": "What is a LAN?",
                    "options": ["Local Area Network", "Large Area Network", "Long Area Network", "Limited Area Network"],
                    "correct_answer": "Local Area Network",
                    "concept": "Network Types",
                    "type": "mcq"
                }
            ],
            "Unit 2": [
                {
                    "question": "What is error detection in data link layer?",
                    "options": ["Finding errors", "Correcting errors", "Preventing errors", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "Error Detection",
                    "type": "mcq"
                },
                {
                    "question": "Which protocol provides reliable data transfer?",
                    "options": ["UDP", "TCP", "IP", "ARP"],
                    "correct_answer": "TCP",
                    "concept": "Transport Layer",
                    "type": "mcq"
                }
            ]
        },
        "315323-SOFTWARE ENGINEERING": {
            "Unit 1": [
                {
                    "question": "What is the first phase of software development life cycle?",
                    "options": ["Design", "Analysis", "Coding", "Testing"],
                    "correct_answer": "Analysis",
                    "concept": "Software Life Cycle",
                    "type": "mcq"
                },
                {
                    "question": "Which model is iterative and incremental?",
                    "options": ["Waterfall", "Spiral", "Agile", "V-Model"],
                    "correct_answer": "Spiral",
                    "concept": "Software Process Models",
                    "type": "mcq"
                },
                {
                    "question": "What is requirements engineering?",
                    "options": ["Coding", "Testing", "Gathering requirements", "Deployment"],
                    "correct_answer": "Gathering requirements",
                    "concept": "Requirements Engineering",
                    "type": "mcq"
                },
                {
                    "question": "Which diagram shows system processes?",
                    "options": ["ER Diagram", "DFD", "Class Diagram", "Use Case Diagram"],
                    "correct_answer": "DFD",
                    "concept": "System Analysis",
                    "type": "mcq"
                },
                {
                    "question": "What is UML?",
                    "options": ["Programming language", "Modeling language", "Database", "Operating system"],
                    "correct_answer": "Modeling language",
                    "concept": "UML Diagrams",
                    "type": "mcq"
                }
            ],
            "Unit 2": [
                {
                    "question": "What is system analysis?",
                    "options": ["Understanding system requirements", "Coding", "Testing", "Deployment"],
                    "correct_answer": "Understanding system requirements",
                    "concept": "System Analysis",
                    "type": "mcq"
                },
                {
                    "question": "Which diagram shows data relationships?",
                    "options": ["DFD", "ER Diagram", "Class Diagram", "Use Case Diagram"],
                    "correct_answer": "ER Diagram",
                    "concept": "Entity Relationship Diagrams",
                    "type": "mcq"
                }
            ],
            "Unit 3": [
                {
                    "question": "What is object-oriented analysis?",
                    "options": ["Analyzing objects", "Analyzing classes", "Analyzing system using objects", "Analyzing data"],
                    "correct_answer": "Analyzing system using objects",
                    "concept": "Object-Oriented Analysis",
                    "type": "mcq"
                },
                {
                    "question": "Which UML diagram shows system actors?",
                    "options": ["Class Diagram", "Use Case Diagram", "Sequence Diagram", "Activity Diagram"],
                    "correct_answer": "Use Case Diagram",
                    "concept": "UML Diagrams",
                    "type": "mcq"
                }
            ],
            "Unit 4": [
                {
                    "question": "What is software testing?",
                    "options": ["Finding bugs", "Fixing bugs", "Preventing bugs", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "Software Testing",
                    "type": "mcq"
                },
                {
                    "question": "Which testing is done by developers?",
                    "options": ["Unit Testing", "Integration Testing", "System Testing", "Acceptance Testing"],
                    "correct_answer": "Unit Testing",
                    "concept": "Testing Strategies",
                    "type": "mcq"
                }
            ],
            "Unit 5": [
                {
                    "question": "What is software maintenance?",
                    "options": ["Fixing bugs", "Adding features", "Updating software", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "Software Maintenance",
                    "type": "mcq"
                },
                {
                    "question": "What is software quality?",
                    "options": ["Meeting requirements", "Being bug-free", "User satisfaction", "All of the above"],
                    "correct_answer": "All of the above",
                    "concept": "Software Quality",
                    "type": "mcq"
                }
            ]
        }
    }
    
    return fallback_db.get(subject, {}).get(unit, [])

@router.post("/evaluate_quiz")
async def evaluate_quiz(submission: QuizSubmission):
    """Evaluate quiz responses and identify mistakes"""
    try:
        # Load the original quiz
        quiz_file = QUIZZES_DIR / submission.subject / f"{submission.unit.replace(' ', '_')}.json"
        
        if not quiz_file.exists():
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        with open(quiz_file, 'r', encoding='utf-8') as f:
            quiz_questions = json.load(f)
        
        # Evaluate responses
        mistakes = []
        correct_count = 0
        total_questions = len(submission.responses)
        
        for question_id, user_answer in submission.responses.items():
            question = quiz_questions[int(question_id)]
            
            if user_answer == question["correct_answer"]:
                correct_count += 1
            else:
                # Get study resources for the missed concept
                study_resources = await _get_study_resources_for_concept(submission.subject, question["concept"])
                
                mistakes.append({
                    "concept": question["concept"],
                    "correct_answer": question["correct_answer"],
                    "user_answer": user_answer,
                    "study_resources": study_resources
                })
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            "subject": submission.subject,
            "unit": submission.unit,
            "score": score,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "mistakes": mistakes
        }
        
    except Exception as e:
        logger.error(f"Error evaluating quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to evaluate quiz: {str(e)}")

async def _get_study_resources_for_concept(subject: str, concept: str) -> List[Dict[str, str]]:
    """Get study resources for a specific concept"""
    # Check cache first
    cache_file = MATERIAL_CACHE_DIR / subject / f"{concept.replace(' ', '_')}_resources.json"
    
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Generate new resources
    resources = [
        {
            "title": f"{concept} - Study Guide",
            "url": f"https://study.com/{concept.lower().replace(' ', '-')}",
            "type": "article",
            "description": f"Comprehensive guide for {concept}"
        },
        {
            "title": f"{concept} - Video Tutorial",
            "url": f"https://youtube.com/watch?v={concept.lower().replace(' ', '')}",
            "type": "video",
            "description": f"Video explanation of {concept}"
        },
        {
            "title": f"{concept} - Practice Questions",
            "url": f"https://practice.com/{concept.lower().replace(' ', '-')}",
            "type": "practice",
            "description": f"Practice questions for {concept}"
        }
    ]
    
    # Cache the resources
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)
    
    return resources

@router.post("/generate_report")
async def generate_report(subject: str, unit: str, evaluation_result: dict):
    """Generate a comprehensive PDF report"""
    try:
        if not PDF_AVAILABLE:
            raise HTTPException(status_code=500, detail="PDF generation not available")
        
        # Create report content
        report_data = {
            "subject": subject,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "score": evaluation_result["score"],
            "total_questions": evaluation_result["total_questions"],
            "correct_count": evaluation_result["correct_count"],
            "mistakes": evaluation_result["mistakes"]
        }
        
        # Generate PDF
        report_filename = f"report_{subject}_{unit}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = REPORTS_DIR / report_filename
        
        _generate_pdf_report(report_path, report_data)
        
        return {
            "report_filename": report_filename,
            "report_path": str(report_path),
            "download_url": f"/study/download_report/{report_filename}"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

def _generate_pdf_report(file_path: Path, data: dict):
    """Generate PDF report using reportlab"""
    doc = SimpleDocTemplate(str(file_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    story.append(Paragraph(f"Study Report - {data['subject']}", title_style))
    story.append(Paragraph(f"Unit: {data['unit']}", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Score Summary
    story.append(Paragraph("Performance Summary", styles['Heading3']))
    score_data = [
        ['Metric', 'Value'],
        ['Score', f"{data['score']:.1f}%"],
        ['Correct Answers', f"{data['correct_count']}/{data['total_questions']}"],
        ['Date', datetime.fromisoformat(data['timestamp']).strftime('%B %d, %Y')]
    ]
    
    score_table = Table(score_data)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(score_table)
    story.append(Spacer(1, 20))
    
    # Mistakes Analysis
    if data['mistakes']:
        story.append(Paragraph("Areas for Improvement", styles['Heading3']))
        
        for mistake in data['mistakes']:
            story.append(Paragraph(f"<b>Concept: {mistake['concept']}</b>", styles['Normal']))
            story.append(Paragraph(f"Your Answer: {mistake['user_answer']}", styles['Normal']))
            story.append(Paragraph(f"Correct Answer: {mistake['correct_answer']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Study Resources
            story.append(Paragraph("Recommended Study Resources:", styles['Normal']))
            for resource in mistake['study_resources'][:3]:  # Top 3 resources
                story.append(Paragraph(f"• {resource['title']} - {resource['url']}", styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(story)

@router.get("/download_report/{filename}")
async def download_report(filename: str):
    """Download generated PDF report"""
    report_path = REPORTS_DIR / filename
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"file_path": str(report_path)} 